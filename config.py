"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    """Класс конфигурации приложения."""
    
    # API ключи
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    
    # OpenRouter настройки
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    IMAGE_MODEL = "google/gemini-2.5-flash-image"
    PROMPT_MODEL = "openai/gpt-4o-mini"
    
    # Настройки приложения
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Настройки для изображений DALL-E 3
    IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', 1024))
    IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', 1024))
    DEFAULT_IMAGE_SIZE = f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}"
    DEFAULT_IMAGE_QUALITY = os.getenv('IMAGE_QUALITY', 'hd')
    DEFAULT_IMAGE_STYLE = os.getenv('IMAGE_STYLE', 'vivid')
    
    # Настройки Flask
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def validate():
        """
        Валидация обязательных настроек.
        
        Raises:
            ValueError: Если отсутствуют обязательные переменные
        """
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY не установлен в .env файле")
        
        return True


# Экземпляр конфигурации
config = Config()

# Валидируем конфигурацию при импорте в режиме DEBUG
if config.DEBUG:
    try:
        config.validate()
        print("✅ Конфигурация успешно загружена")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")