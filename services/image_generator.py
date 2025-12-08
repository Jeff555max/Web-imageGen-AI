"""
Сервис для генерации изображений с помощью Gemini 2.5 Flash Image через OpenRouter.
"""

import requests
from typing import Dict, Optional
from io import BytesIO
from PIL import Image
import base64
from datetime import datetime
from config import config


class ImageGenerator:
    """Класс для генерации изображений с использованием Gemini 2.5 Flash Image через OpenRouter."""
    
    # Доступные размеры
    AVAILABLE_SIZES = ["1024x1024", "1024x1792", "1792x1024"]
    
    # Доступные качества
    AVAILABLE_QUALITIES = ["standard", "hd", "low", "medium", "high", "auto"]
    
    # Доступные стили
    AVAILABLE_STYLES = ["vivid", "natural"]
    
    def __init__(self):
        """Инициализация клиента OpenRouter."""
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.IMAGE_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Web Image Generator AI"
        }
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "auto",
        style: str = "vivid"
    ) -> Dict:
        """
        Генерирует изображение с помощью Gemini 2.5 Flash Image.
        
        Args:
            prompt: Текстовое описание изображения
            size: Размер изображения (1024x1024, 1024x1792, 1792x1024)
            quality: Качество изображения
            style: Стиль изображения (vivid, natural)
            
        Returns:
            Словарь с информацией о сгенерированном изображении
        """
        try:
            # Валидация параметров
            if size not in self.AVAILABLE_SIZES:
                size = "1024x1024"
            if quality not in self.AVAILABLE_QUALITIES:
                quality = "auto"
            if style not in self.AVAILABLE_STYLES:
                style = "vivid"
            
            # Конвертируем размер в aspect_ratio для Gemini
            aspect_ratio_map = {
                "1024x1024": "1:1",
                "1024x1792": "9:16",  # Портретный
                "1792x1024": "16:9"   # Альбомный
            }
            aspect_ratio = aspect_ratio_map.get(size, "1:1")
            
            # Запрос к Gemini 2.5 Flash Image через OpenRouter
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "modalities": ["image", "text"],
                    "image_config": {
                        "aspect_ratio": aspect_ratio
                    }
                },
                timeout=120
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Получаем результат
            message = data.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "")
            
            image_url = None
            revised_prompt = prompt
            
            # Проверяем разные форматы ответа
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "image_url":
                            image_url = item.get("image_url", {}).get("url")
                        elif "image_url" in item:
                            img_data = item["image_url"]
                            image_url = img_data.get("url") if isinstance(img_data, dict) else img_data
            elif isinstance(content, str):
                # Контент может содержать текст или base64 изображение
                if content.startswith("data:image"):
                    image_url = content
                else:
                    revised_prompt = content
            
            # Проверяем наличие изображений в других полях
            if not image_url:
                # Проверяем поле images в message (формат Gemini/OpenRouter)
                images = message.get("images", [])
                if images:
                    img = images[0]
                    if isinstance(img, dict):
                        # Формат: {"type": "image_url", "image_url": {"url": "..."}}
                        img_url_data = img.get("image_url", {})
                        if isinstance(img_url_data, dict):
                            image_url = img_url_data.get("url")
                        else:
                            image_url = img_url_data
                    else:
                        image_url = img
                
                # Проверяем поле data (формат DALL-E)
                if not image_url:
                    image_data = data.get("data", [])
                    if image_data:
                        img = image_data[0]
                        if isinstance(img, dict):
                            image_url = img.get("url") or img.get("b64_json")
                            if img.get("b64_json"):
                                image_url = f"data:image/png;base64,{img['b64_json']}"
                            revised_prompt = img.get("revised_prompt", revised_prompt)
            
            return {
                "success": True,
                "url": image_url,
                "revised_prompt": revised_prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "original_prompt": prompt
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
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
        """
        clean_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_'))
        clean_prompt = clean_prompt.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"image_{clean_prompt}_{timestamp}.png"
