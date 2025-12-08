"""
Сервис для улучшения промптов с помощью GPT-4o-mini через OpenRouter.
"""

import requests
from typing import Dict
from config import config


class PromptEnhancer:
    """Класс для улучшения пользовательских промптов с использованием GPT-4o-mini."""
    
    # Словарь системных промптов для различных стилей
    STYLE_PROMPTS = {
        "без_стиля": {
            "system": """Улучши промпт пользователя для генерации изображения, сохраняя естественность и реалистичность.
Добавь только необходимые детали качества и композиции.
Не навязывай конкретный художественный стиль.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", high quality, detailed, photorealistic"
        },
        
        "реалистичный": {
            "system": """Улучши промпт для создания максимально реалистичного изображения.
Добавь детали освещения, текстур, анатомической точности.
Фокус на фотореалистичности и естественности.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", photorealistic, high detail, natural lighting, realistic textures, 8K resolution"
        },
        
        "аниме": {
            "system": """Адаптируй промпт под аниме стиль.
Добавь характерные черты: большие выразительные глаза, яркие цвета, динамичные позы.
Укажи качество в стиле японской анимации.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", anime style, manga art, vibrant colors, expressive eyes, cel shading"
        },
        
        "киберпанк": {
            "system": """Преобразуй промпт в киберпанк эстетику.
Добавь неоновое освещение, футуристические элементы, темную атмосферу.
Включи технологические детали и урбанистический фон.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", cyberpunk style, neon lights, futuristic, dark atmosphere, high-tech, urban"
        },
        
        "фэнтези": {
            "system": """Адаптируй промпт под фэнтези стиль.
Добавь магические элементы, мифических существ, средневековую атмосферу.
Включи драматичное освещение и эпическую композицию.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", fantasy art, magical atmosphere, epic composition, dramatic lighting, mystical"
        },
        
        "акварель": {
            "system": """Преобразуй промпт в стиль акварельной живописи.
Добавь характерные черты: мягкие переходы, прозрачность, текучесть красок.
Укажи на традиционную акварельную технику.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", watercolor painting, soft brushstrokes, transparent washes, artistic, traditional art"
        },
        
        "масляная_живопись": {
            "system": """Адаптируй промпт под стиль масляной живописи.
Добавь характерные мазки кисти, насыщенные цвета, классическую композицию.
Включи элементы традиционной живописи.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", oil painting, classical art, rich colors, visible brushstrokes, fine art"
        },
        
        "эскиз": {
            "system": """Преобразуй промпт в стиль художественного эскиза.
Добавь характерные черты: линейность, наброски, карандашная техника.
Фокус на контурах и композиции.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", pencil sketch, line art, artistic drawing, monochrome, hand-drawn"
        },
        
        "3d_рендер": {
            "system": """Адаптируй промпт под 3D рендеринг.
Добавь объемность, современное освещение, цифровую эстетику.
Включи элементы компьютерной графики высокого качества.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", 3D render, digital art, volumetric lighting, high poly, cinema 4d style"
        },
        
        "винтаж": {
            "system": """Преобразуй промпт в винтажный стиль.
Добавь ретро элементы, приглушенные цвета, классическую эстетику.
Включи атмосферу определенной исторической эпохи.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", vintage style, retro aesthetic, muted colors, classic composition, nostalgic"
        },
        
        "минимализм": {
            "system": """Адаптируй промпт под минималистичный стиль.
Упрости композицию, используй чистые линии, ограниченную цветовую палитру.
Фокус на простоте и элегантности.
Отвечай ТОЛЬКО улучшенным промптом на английском языке, без дополнительных пояснений.""",
            "suffix": ", minimalist design, clean lines, simple composition, limited color palette, elegant"
        }
    }
    
    def __init__(self):
        """Инициализация клиента OpenRouter."""
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.PROMPT_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Web Image Generator AI"
        }
    
    def enhance_prompt(self, user_prompt: str, style: str = "без_стиля") -> Dict[str, str]:
        """
        Улучшает пользовательский промпт с учетом выбранного стиля.
        """
        try:
            style_config = self.STYLE_PROMPTS.get(style, self.STYLE_PROMPTS["без_стиля"])
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": style_config["system"]},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            enhanced_prompt = data["choices"][0]["message"]["content"].strip()
            final_prompt = f"{enhanced_prompt}{style_config['suffix']}"
            
            return {
                "original": user_prompt,
                "enhanced": final_prompt,
                "style": style
            }
            
        except Exception as e:
            return {
                "original": user_prompt,
                "enhanced": user_prompt,
                "style": style,
                "error": str(e)
            }
    
    def enhance_for_correction(self, original_prompt: str, correction: str) -> str:
        """
        Создает промпт для исправления существующего изображения.
        """
        try:
            system_prompt = """Ты помогаешь создавать промпты для модификации изображений.
На основе оригинального описания и желаемых изменений создай новый промпт.
Сохрани основную концепцию, но добавь запрошенные изменения.
Отвечай ТОЛЬКО новым промптом на английском языке."""
            
            user_message = f"""Оригинальное описание изображения: {original_prompt}

Желаемые изменения: {correction}

Создай новый промпт, который сохранит основную идею, но учтет изменения."""
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 250
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            return f"{original_prompt}. Modified: {correction}"
