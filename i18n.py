"""
Модуль интернационализации (i18n) для Speech Manager.

Поддерживает переводы статусных сообщений на разные языки.
"""

from typing import Dict, Optional

# Переводы статусных сообщений
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ru": {
        "ready": "⏸️ Готов...",
        "listening": "🎤 Слушаю...",
        "recognizing": "⏳ Распознаю...",
        "done": "✅ Готово!",
        "not_understood": "❌ Не распознано",
        "network_error": "❌ Ошибка сети",
        "error": "❌ Ошибка",
        "audio_error": "❌ Ошибка аудио",
    },
    "en": {
        "ready": "⏸️ Ready...",
        "listening": "🎤 Listening...",
        "recognizing": "⏳ Recognizing...",
        "done": "✅ Done!",
        "not_understood": "❌ Not understood",
        "network_error": "❌ Network error",
        "error": "❌ Error",
        "audio_error": "❌ Audio error",
    },
    "uk": {
        "ready": "⏸️ Готово...",
        "listening": "🎤 Слухаю...",
        "recognizing": "⏳ Розпізнаю...",
        "done": "✅ Готово!",
        "not_understood": "❌ Не розпізнано",
        "network_error": "❌ Помилка мережі",
        "error": "❌ Помилка",
        "audio_error": "❌ Помилка аудіо",
    },
    "de": {
        "ready": "⏸️ Bereit...",
        "listening": "🎤 Höre zu...",
        "recognizing": "⏳ Erkenne...",
        "done": "✅ Fertig!",
        "not_understood": "❌ Nicht verstanden",
        "network_error": "❌ Netzwerkfehler",
        "error": "❌ Fehler",
        "audio_error": "❌ Audiofehler",
    },
    "fr": {
        "ready": "⏸️ Prêt...",
        "listening": "🎤 Écoute...",
        "recognizing": "⏳ Reconnaissance...",
        "done": "✅ Terminé!",
        "not_understood": "❌ Non compris",
        "network_error": "❌ Erreur réseau",
        "error": "❌ Erreur",
        "audio_error": "❌ Erreur audio",
    },
    "es": {
        "ready": "⏸️ Listo...",
        "listening": "🎤 Escuchando...",
        "recognizing": "⏳ Reconociendo...",
        "done": "✅ ¡Hecho!",
        "not_understood": "❌ No entendido",
        "network_error": "❌ Error de red",
        "error": "❌ Error",
        "audio_error": "❌ Error de audio",
    },
}

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"

# Поддерживаемые языки
SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())


def get_status_text(key: str, language: Optional[str] = None) -> str:
    """
    Получает переведенный текст статуса.
    
    Args:
        key: Ключ статуса (ready, listening, recognizing, done, etc.)
        language: Код языка (ru, en, uk, de, fr, es). Если None, используется DEFAULT_LANGUAGE
        
    Returns:
        Переведенный текст или ключ, если перевод не найден
    """
    if language is None:
        language = DEFAULT_LANGUAGE
    
    # Нормализуем ключ (lowercase, без пробелов)
    key = key.lower().strip().replace(" ", "_")
    
    # Маппинг языков без переводов на поддерживаемые
    # Если язык не поддерживается, используем английский как fallback
    language_fallback = {
        'pl': 'en',  # Polish -> English
        'it': 'en',  # Italian -> English
        'ja': 'en',  # Japanese -> English
        'ko': 'en',  # Korean -> English
        'zh': 'en',  # Chinese -> English
    }
    
    # Если язык не поддерживается, используем fallback
    if language not in SUPPORTED_LANGUAGES:
        language = language_fallback.get(language, DEFAULT_LANGUAGE)
    
    # Получаем переводы для языка
    translations = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])
    
    # Возвращаем перевод или ключ, если не найден
    return translations.get(key, key)


def set_language(language: str) -> bool:
    """
    Устанавливает язык по умолчанию.
    
    Args:
        language: Код языка (ru, en, uk, de, fr, es)
        
    Returns:
        True если язык установлен, False если язык не поддерживается
    """
    global DEFAULT_LANGUAGE
    if language in SUPPORTED_LANGUAGES:
        DEFAULT_LANGUAGE = language
        return True
    return False


def get_supported_languages() -> list:
    """Возвращает список поддерживаемых языков."""
    return SUPPORTED_LANGUAGES.copy()


def detect_system_language() -> str:
    """
    Определяет язык системы.
    
    Returns:
        Код языка системы или DEFAULT_LANGUAGE, если не удалось определить
    """
    try:
        import locale
        system_lang = locale.getdefaultlocale()[0]
        if system_lang:
            # Извлекаем код языка (например, 'ru_RU' -> 'ru')
            lang_code = system_lang.split('_')[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    except Exception:
        pass
    
    return DEFAULT_LANGUAGE
