"""
Главное Flask приложение для генерации изображений.
"""

from flask import Flask, render_template, request, jsonify, send_file
from services.prompt_enhancer import PromptEnhancer
from services.image_generator import ImageGenerator
from config import config
import os
from io import BytesIO


# Создание Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


# Инициализация сервисов
prompt_enhancer = PromptEnhancer()
image_generator = ImageGenerator()


@app.route('/')
def index():
    """
    Главная страница приложения.
    
    Returns:
        HTML шаблон главной страницы
    """
    return render_template('index.html')


@app.route('/api/enhance-prompt', methods=['POST'])
def enhance_prompt():
    """
    API endpoint для улучшения пользовательского промпта.
    
    Принимает JSON с полями:
        - prompt: текстовое описание от пользователя
        - style: выбранный стиль изображения
    
    Returns:
        JSON с оригинальным и улучшенным промптом
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Промпт не может быть пустым'
            }), 400
        
        user_prompt = data['prompt'].strip()
        style = data.get('style', 'без_стиля')
        
        if not user_prompt:
            return jsonify({
                'success': False,
                'error': 'Промпт не может быть пустым'
            }), 400
        
        # Улучшаем промпт
        result = prompt_enhancer.enhance_prompt(user_prompt, style)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'original_prompt': result['original'],
            'enhanced_prompt': result['enhanced'],
            'style': result['style']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    API endpoint для генерации изображения.
    
    Принимает JSON с полями:
        - prompt: текстовое описание изображения
        - size: размер изображения (опционально)
        - quality: качество изображения (опционально)
        - style: стиль изображения DALL-E (vivid/natural, опционально)
    
    Returns:
        JSON с URL сгенерированного изображения и метаданными
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Промпт не может быть пустым'
            }), 400
        
        prompt = data['prompt'].strip()
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'hd')
        dalle_style = data.get('dalle_style', 'vivid')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Промпт не может быть пустым'
            }), 400
        
        # Генерируем изображение
        result = image_generator.generate_image(
            prompt=prompt,
            size=size,
            quality=quality,
            style=dalle_style
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Неизвестная ошибка при генерации')
            }), 500
        
        return jsonify({
            'success': True,
            'image_url': result['url'],
            'revised_prompt': result.get('revised_prompt'),
            'original_prompt': result['original_prompt'],
            'size': result['size'],
            'quality': result['quality']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/enhance-for-correction', methods=['POST'])
def enhance_for_correction():
    """
    API endpoint для создания промпта исправления изображения.
    
    Принимает JSON с полями:
        - original_prompt: оригинальный промпт
        - correction: описание желаемых изменений
    
    Returns:
        JSON с новым промптом для генерации
    """
    try:
        data = request.get_json()
        
        if not data or 'original_prompt' not in data or 'correction' not in data:
            return jsonify({
                'success': False,
                'error': 'Необходимы оригинальный промпт и описание изменений'
            }), 400
        
        original_prompt = data['original_prompt'].strip()
        correction = data['correction'].strip()
        
        if not original_prompt or not correction:
            return jsonify({
                'success': False,
                'error': 'Поля не могут быть пустыми'
            }), 400
        
        # Создаем промпт для исправления
        corrected_prompt = prompt_enhancer.enhance_for_correction(
            original_prompt,
            correction
        )
        
        return jsonify({
            'success': True,
            'corrected_prompt': corrected_prompt
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404."""
    return jsonify({'error': 'Страница не найдена'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500."""
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


if __name__ == '__main__':
    # Запуск приложения
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )
