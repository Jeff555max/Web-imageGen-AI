"""
Сервис для генерации изображений с помощью GPT-5 Image Mini через OpenRouter.
"""

from openai import OpenAI
from typing import Dict, Optional
import requests
from io import BytesIO
from PIL import Image
import base64
from datetime import datetime
from config import config


class ImageGenerator:
    """Класс для генерации изображений с использованием GPT-5 Image Mini через OpenRouter."""
    
    # Доступные размеры
    AVAILABLE_SIZES = ["1024x1024", "1024x1792", "1792x1024"]
    
    # Доступные качества
    AVAILABLE_QUALITIES = ["standard", "hd", "low", "medium", "high", "auto"]
    
    # Доступные стили
    AVAILABLE_STYLES = ["vivid", "natural"]
    
    def __init__(self):
        """Инициализация клиента OpenRouter."""
        self.client = OpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL
        )
        self.model = config.IMAGE_MODEL
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "hd",
        style: str = "vivid"
    ) -> Dict:
        """
        Генерирует изображение с помощью DALL-E 3.
        
        Args:
            prompt: Текстовое описание изображения
            size: Размер изображения (1024x1024, 1024x1792, 1792x1024)
            quality: Качество изображения (standard, hd)
            style: Стиль изображения (vivid, natural)
            
        Returns:
            Словарь с информацией о сгенерированном изображении
        """
        try:
            # Валидация параметров
            if size not in self.AVAILABLE_SIZES:
                size = "1024x1024"
            if quality not in self.AVAILABLE_QUALITIES:
                quality = "hd"
            if style not in self.AVAILABLE_STYLES:
                style = "vivid"
            
            # Запрос к GPT-5 Image Mini через OpenRouter
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate an image: {prompt}"
                    }
                ],
                extra_body={
                    "image_generation": {
                        "size": size,
                        "quality": quality if quality in ["low", "medium", "high", "auto"] else "auto"
                    }
                }
            )
            
            # Получаем результат - изображение в base64 из ответа
            message = response.choices[0].message
            image_url = None
            revised_prompt = prompt
            
            # Проверяем наличие изображения в ответе
            if hasattr(message, 'content') and message.content:
                # Ищем URL изображения в контенте
                if isinstance(message.content, list):
                    for content_part in message.content:
                        if hasattr(content_part, 'type') and content_part.type == 'image_url':
                            image_url = content_part.image_url.url
                        elif hasattr(content_part, 'image_url'):
                            image_url = content_part.image_url.get('url') if isinstance(content_part.image_url, dict) else content_part.image_url.url
                elif isinstance(message.content, str):
                    revised_prompt = message.content
            
            # Проверяем также атрибут images если есть
            if hasattr(response, 'images') and response.images:
                image_url = response.images[0].url if hasattr(response.images[0], 'url') else response.images[0]
            
            # Альтернативная проверка через data
            if not image_url and hasattr(response, 'data') and response.data:
                for item in response.data:
                    if hasattr(item, 'url'):
                        image_url = item.url
                        break
                    if hasattr(item, 'b64_json'):
                        image_url = f"data:image/png;base64,{item.b64_json}"
                        break
            
            return {
                "success": True,
                "url": image_url,
                "revised_prompt": revised_prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "original_prompt": prompt
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_prompt": prompt
            }
    
    def download_image(self, url: str) -> Optional[BytesIO]:
        """
        Скачивает изображение по URL.
        
        Args:
            url: URL изображения
            
        Returns:
            BytesIO объект с изображением или None в случае ошибки
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return BytesIO(response.content)
        except Exception as e:
            print(f"Ошибка при скачивании изображения: {e}")
            return None
    
    def image_to_base64(self, image_url: str) -> Optional[str]:
        """
        Конвертирует изображение по URL в base64 строку.
        
        Args:
            image_url: URL изображения
            
        Returns:
            Base64 строка изображения или None
        """
        try:
            image_data = self.download_image(image_url)
            if image_data:
                image = Image.open(image_data)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"data:image/png;base64,{img_str}"
            return None
        except Exception as e:
            print(f"Ошибка при конвертации в base64: {e}")
            return None
    
    @staticmethod
    def generate_filename(prompt: str) -> str:
        """
        Генерирует имя файла на основе промпта и времени.
        
        Args:
            prompt: Текстовое описание изображения
            
        Returns:
            Имя файла для сохранения
        """
        # Берем первые 30 символов промпта, очищаем от спецсимволов
        clean_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_'))
        clean_prompt = clean_prompt.replace(' ', '_')
        
        # Добавляем временную метку
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"dalle3_{clean_prompt}_{timestamp}.png"
