/**
 * Главный JavaScript файл для Web Image Generator AI
 */

// Глобальные переменные
let currentEnhancedPrompt = null;
let currentOriginalPrompt = null;
let currentImageUrl = null;

// Элементы DOM
const userPrompt = document.getElementById('userPrompt');
const charCount = document.getElementById('charCount');
const imageStyle = document.getElementById('imageStyle');
const imageSize = document.getElementById('imageSize');
const enhanceBtn = document.getElementById('enhanceBtn');
const generateBtn = document.getElementById('generateBtn');
const enhancedPromptSection = document.getElementById('enhancedPromptSection');
const enhancedPromptText = document.getElementById('enhancedPromptText');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
const generatedImage = document.getElementById('generatedImage');
const usedPrompt = document.getElementById('usedPrompt');
const downloadBtn = document.getElementById('downloadBtn');
const createNewBtn = document.getElementById('createNewBtn');
const showCorrectionBtn = document.getElementById('showCorrectionBtn');
const correctionPanel = document.getElementById('correctionPanel');
const correctionPrompt = document.getElementById('correctionPrompt');
const applyCorrectionBtn = document.getElementById('applyCorrectionBtn');
const imageModal = new bootstrap.Modal(document.getElementById('imageModal'));
const modalImage = document.getElementById('modalImage');

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

/**
 * Настройка обработчиков событий
 */
function setupEventListeners() {
    // Счетчик символов
    userPrompt.addEventListener('input', updateCharCount);
    
    // Кнопка улучшения промпта
    enhanceBtn.addEventListener('click', handleEnhancePrompt);
    
    // Кнопка генерации
    generateBtn.addEventListener('click', handleGenerateImage);
    
    // Кнопка скачивания
    downloadBtn.addEventListener('click', handleDownloadImage);
    
    // Кнопка создания нового
    createNewBtn.addEventListener('click', handleCreateNew);
    
    // Показ панели исправления
    showCorrectionBtn.addEventListener('click', toggleCorrectionPanel);
    
    // Применение исправлений
    applyCorrectionBtn.addEventListener('click', handleApplyCorrection);
    
    // Увеличение изображения по клику
    generatedImage.addEventListener('click', () => {
        modalImage.src = generatedImage.src;
        imageModal.show();
    });
    
    // Enter для улучшения (Ctrl+Enter)
    userPrompt.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            handleEnhancePrompt();
        }
    });
}

/**
 * Обновление счетчика символов
 */
function updateCharCount() {
    const count = userPrompt.value.length;
    charCount.textContent = count;
    
    if (count > 0) {
        enhanceBtn.disabled = false;
        generateBtn.disabled = false;
    } else {
        enhanceBtn.disabled = true;
        generateBtn.disabled = true;
    }
}

/**
 * Обработка улучшения промпта
 */
async function handleEnhancePrompt() {
    const prompt = userPrompt.value.trim();
    const style = imageStyle.value;
    
    if (!prompt) {
        showNotification('Пожалуйста, введите описание изображения', 'warning');
        return;
    }
    
    // Отключаем кнопки
    enhanceBtn.disabled = true;
    enhanceBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Улучшаем...';
    
    try {
        const response = await fetch('/api/enhance-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt, style })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentEnhancedPrompt = data.enhanced_prompt;
            currentOriginalPrompt = data.original_prompt;
            
            // Показываем улучшенный промпт
            enhancedPromptText.textContent = data.enhanced_prompt;
            enhancedPromptSection.style.display = 'block';
            enhancedPromptSection.classList.add('fade-in');
            
            // Активируем кнопку генерации
            generateBtn.disabled = false;
            
            showNotification('Промпт успешно улучшен!', 'success');
        } else {
            showNotification('Ошибка при улучшении промпта: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Ошибка соединения с сервером', 'danger');
        console.error(error);
    } finally {
        enhanceBtn.disabled = false;
        enhanceBtn.innerHTML = '✨ Улучшить промпт (опционально)';
    }
}

/**
 * Обработка генерации изображения
 */
async function handleGenerateImage() {
    // Используем улучшенный промпт или оригинальный
    const promptToUse = currentEnhancedPrompt || userPrompt.value.trim();
    
    if (!promptToUse) {
        showNotification('Введите описание изображения', 'warning');
        return;
    }
    
    // Получаем выбранный размер
    const selectedSize = imageSize ? imageSize.value : '1024x1024';
    
    // Скрываем предыдущий результат
    resultSection.style.display = 'none';
    
    // Показываем прогресс бар
    progressSection.style.display = 'block';
    updateProgress(10, 'Отправка запроса...');
    
    // Отключаем кнопки
    generateBtn.disabled = true;
    enhanceBtn.disabled = true;
    
    try {
        updateProgress(30, 'Генерация изображения...');
        
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: promptToUse,
                size: selectedSize,
                quality: 'auto',
                dalle_style: 'vivid'
            })
        });
        
        updateProgress(70, 'Получение результата...');
        
        const data = await response.json();
        
        if (data.success) {
            updateProgress(90, 'Загрузка изображения...');
            
            currentImageUrl = data.image_url;
            
            // Отображаем изображение
            generatedImage.src = data.image_url;
            usedPrompt.textContent = promptToUse;
            
            updateProgress(100, 'Готово!');
            
            setTimeout(() => {
                progressSection.style.display = 'none';
                resultSection.style.display = 'block';
                resultSection.classList.add('fade-in');
                resetProgress();
            }, 500);
            
            showNotification('Изображение успешно сгенерировано!', 'success');
        } else {
            progressSection.style.display = 'none';
            showNotification('Ошибка при генерации: ' + data.error, 'danger');
        }
    } catch (error) {
        progressSection.style.display = 'none';
        showNotification('Ошибка соединения с сервером', 'danger');
        console.error(error);
    } finally {
        generateBtn.disabled = false;
        enhanceBtn.disabled = false;
    }
}

/**
 * Обработка скачивания изображения
 */
function handleDownloadImage() {
    if (!currentImageUrl) return;
    
    const link = document.createElement('a');
    link.href = currentImageUrl;
    link.download = `dalle_image_${Date.now()}.png`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Изображение загружено!', 'success');
}

/**
 * Обработка создания нового изображения
 */
function handleCreateNew() {
    userPrompt.value = '';
    updateCharCount();
    enhancedPromptSection.style.display = 'none';
    resultSection.style.display = 'none';
    correctionPanel.style.display = 'none';
    correctionPrompt.value = '';
    currentEnhancedPrompt = null;
    currentOriginalPrompt = null;
    currentImageUrl = null;
    generateBtn.disabled = true;
    
    userPrompt.focus();
    showNotification('Готов к созданию нового изображения', 'info');
}

/**
 * Переключение панели исправления
 */
function toggleCorrectionPanel() {
    if (correctionPanel.style.display === 'none') {
        correctionPanel.style.display = 'block';
        correctionPanel.classList.add('fade-in');
    } else {
        correctionPanel.style.display = 'none';
    }
}

/**
 * Обработка применения исправлений
 */
async function handleApplyCorrection() {
    const correction = correctionPrompt.value.trim();
    
    if (!correction) {
        showNotification('Опишите желаемые изменения', 'warning');
        return;
    }
    
    const originalPrompt = currentEnhancedPrompt || userPrompt.value.trim();
    
    if (!originalPrompt) {
        showNotification('Нет оригинального промпта', 'danger');
        return;
    }
    
    applyCorrectionBtn.disabled = true;
    applyCorrectionBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Обработка...';
    
    try {
        const response = await fetch('/api/enhance-for-correction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original_prompt: originalPrompt,
                correction: correction
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentEnhancedPrompt = data.corrected_prompt;
            enhancedPromptText.textContent = data.corrected_prompt;
            correctionPanel.style.display = 'none';
            correctionPrompt.value = '';
            
            showNotification('Промпт обновлен! Нажмите "Генерировать изображение"', 'success');
        } else {
            showNotification('Ошибка при создании промпта исправления: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Ошибка соединения с сервером', 'danger');
        console.error(error);
    } finally {
        applyCorrectionBtn.disabled = false;
        applyCorrectionBtn.innerHTML = '✅ Применить изменения';
    }
}

/**
 * Обновление прогресс бара
 */
function updateProgress(percent, text) {
    progressBar.style.width = percent + '%';
    progressText.textContent = text;
}

/**
 * Сброс прогресс бара
 */
function resetProgress() {
    progressBar.style.width = '0%';
    progressText.textContent = 'Инициализация...';
}

/**
 * Показ уведомлений
 */
function showNotification(message, type = 'info') {
    // Создаем toast элемент
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'danger' ? 'danger' : type === 'warning' ? 'warning' : 'primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Создаем контейнер для toast если его нет
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Добавляем toast
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    toastContainer.appendChild(toastElement.firstElementChild);
    
    // Показываем toast
    const toast = new bootstrap.Toast(toastContainer.lastElementChild, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Удаляем после скрытия
    toastContainer.lastElementChild.addEventListener('hidden.bs.toast', () => {
        toastContainer.lastElementChild.remove();
    });
}
