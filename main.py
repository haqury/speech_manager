#!/usr/bin/env python3
"""
Speech Manager - приложение для распознавания речи с выводом в разные места.

Основные возможности:
- Распознавание речи через Google Speech Recognition
- Вывод в UI, буфер обмена, текстовый курсор
- Настраиваемая горячая клавиша
- Системный трей
"""
import sys
import time
import logging
from win32api import GetSystemMetrics
import keyboard
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import config
import state as s
import listner
import speech_recognition as sr
from audio_recorder import MicrophoneStream
import subtitle_speach
from subtitle_speach.status_colors import get_status_style
import settings_window
import i18n

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

# Modern threading для Python 3.14+
from threading_manager import (
    ThreadManager,
    print_threading_info
)

# Logging configuration
from logger_config import setup_logging, get_logger

# Setup logging
setup_logging(log_file='speech_manager.log', level=logging.INFO)
logger = get_logger(__name__)


r = sr.Recognizer()

conf = config.Config()  # Создаем экземпляр Config
state = s.State(conf)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)  # Не закрывать приложение при закрытии окна

# Проверка поддержки системного трея
if not QSystemTrayIcon.isSystemTrayAvailable():
    QMessageBox.critical(None, "Speech Manager", 
                        "Системный трей недоступен на этой системе.")
    sys.exit(1)

# Современная многопоточность для Python 3.14+
thread_manager = ThreadManager()

# Печатаем информацию о режиме многопоточности
print_threading_info()



def process_speech(m: listner.ListnerManger) -> None:
    """
    Процесс распознавания речи.
    Слушает микрофон, распознает речь через Google Speech Recognition
    и выводит результат в UI/буфер обмена/текстовый курсор.
    
    Args:
        m: Экземпляр ListnerManger для обработки распознанного текста
    """
    import time as timing
    total_start = timing.time()
    logger.info("=" * 60)
    logger.info("🎤 Started speech recognition process")

    # Вспомогательная функция для обновления статуса с цветом
    def update_status(text: str, status_key: str) -> None:
        """
        Обновляет текст и цвет статусного лейбла.
        
        Args:
            text: Текст для отображения
            status_key: Ключ статуса для выбора цвета ('listening', 'recognizing', 'on', 'off')
        """
        try:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            font_size = m.window.config.font_size if m.window.config else 30
            style = get_status_style(status_key, font_size)
            
            # Обновляем текст
            QMetaObject.invokeMethod(
                m.window.statelbl,
                "setText",
                Qt.QueuedConnection,
                Q_ARG(str, text)
            )
            # Обновляем стиль (цвет)
            QMetaObject.invokeMethod(
                m.window.statelbl,
                "setStyleSheet",
                Qt.QueuedConnection,
                Q_ARG(str, style)
            )
        except Exception as e:
            logger.error(f"Error updating status to '{text}': {e}", exc_info=True)
    
    # Callback для обновления громкости
    def on_volume_update(volume: int) -> None:
        """
        Вызывается при изменении громкости микрофона.
        
        Args:
            volume: Уровень громкости (0-100)
        """
        try:
            m.window.update_volume(volume)
        except Exception as e:
            logger.error(f"Error updating volume: {e}", exc_info=True)
    
    # Callback функции для синхронизации UI с состоянием записи
    def on_speech_start() -> None:
        """Вызывается когда начинается реальная запись речи."""
        logger.info(f"⏱️  Speech detection started at {timing.time() - total_start:.2f}s")
        # Определяем язык по текущей раскладке клавиатуры Windows
        current_lang = state.get_keyboard_language_code()
        update_status(i18n.get_status_text("listening", current_lang), "listening")

    def on_speech_end() -> None:
        """Вызывается когда заканчивается запись речи."""
        logger.info(f"⏱️  Speech ended at {timing.time() - total_start:.2f}s")

    # Используем MicrophoneStream вместо sr.Microphone (PyAudio заменен на SoundDevice)
    # Используем выбранный микрофон из настроек
    selected_device = m.window.config.selected_mic_index if m.window.config else None
    
    with MicrophoneStream(
        device=selected_device,
        energy_threshold=m.window.config.energy_threshold if m.window.config else 300,
        pause_threshold=m.window.config.pause_threshold if m.window.config else 0.8,
        on_speech_start=on_speech_start,
        on_speech_end=on_speech_end,
        on_volume_update=on_volume_update
    ) as source:
        try:
            # Показываем окно при активации прослушивания
            if not m.window.isVisible():
                m.window.show()
                m.window.activateWindow()
                m.window.raise_()
            
            # Определяем язык по текущей раскладке клавиатуры Windows
            current_lang = state.get_keyboard_language_code()
            update_status(i18n.get_status_text("ready", current_lang), "on")
            # Показываем визуализатор громкости
            m.window.show_volume_bar(True)
            # Сбрасываем таймер скрытия при активации
            if m.window.config and m.window.config.auto_hide_duration > 0:
                m.window.hide_timer.stop()
            
            # Слушаем и распознаем речь
            listen_start = timing.time()
            logger.info(f"⏱️  Starting to listen at {listen_start - total_start:.2f}s...")
            audio_data = source.listen(phrase_time_limit=conf.phrase_time_limit)
            listen_time = timing.time() - listen_start
            logger.info(f"⏱️  Audio captured in {listen_time:.2f}s (includes pause_threshold: {m.window.config.pause_threshold if m.window.config else 0.8}s)")
            
            # Показываем индикатор распознавания
            # Определяем язык по текущей раскладке клавиатуры Windows
            current_lang = state.get_keyboard_language_code()
            update_status(i18n.get_status_text("recognizing", current_lang), "recognizing")
            
            try:
                # Распознаем через Google Speech Recognition
                api_start = timing.time()
                logger.info(f"⏱️  Calling Google API at {api_start - total_start:.2f}s...")
                result = r.recognize_google(audio_data, language=state.get_keyboard_language(), show_all=True)
                api_time = timing.time() - api_start
                logger.info(f"⏱️  Google API responded in {api_time:.2f}s")
                
                # Обрабатываем результат
                process_start = timing.time()
                logger.info(f"⏱️  Processing text at {process_start - total_start:.2f}s...")
                m.process(result)
                process_time = timing.time() - process_start
                logger.info(f"⏱️  Text processed in {process_time:.2f}s")
                
                total_time = timing.time() - total_start
                logger.info(f"✅ TOTAL: {total_time:.2f}s | Listen: {listen_time:.2f}s | API: {api_time:.2f}s | Process: {process_time:.2f}s")
                logger.info(f"📊 Breakdown: pause_threshold={m.window.config.pause_threshold if m.window.config else 0.8}s affects listen time")
                
                # Показываем успешное завершение
                # Определяем язык по текущей раскладке клавиатуры Windows
                current_lang = state.get_keyboard_language_code()
                update_status(i18n.get_status_text("done", current_lang), "on")
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition could not understand audio")
                # Определяем язык по текущей раскладке клавиатуры Windows
                current_lang = state.get_keyboard_language_code()
                update_status(i18n.get_status_text("not_understood", current_lang), "error")
            except sr.RequestError as e:
                logger.error(f"Network error with Google Speech Recognition: {e}", exc_info=True)
                # Определяем язык по текущей раскладке клавиатуры Windows
                current_lang = state.get_keyboard_language_code()
                update_status(i18n.get_status_text("network_error", current_lang), "error")
            except Exception as e:
                logger.error(f"Unexpected error during speech recognition: {e}", exc_info=True)
                # Определяем язык по текущей раскладке клавиатуры Windows
                current_lang = state.get_keyboard_language_code()
                update_status(i18n.get_status_text("error", current_lang), "error")
            
            # Скрываем визуализатор громкости и сбрасываем значение
            m.window.show_volume_bar(False)
            m.window.update_volume(0)
            
            # Запускаем таймер скрытия после окончания прослушивания
            if m.window.config and m.window.config.auto_hide_duration > 0:
                m.window.schedule_auto_hide()
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            # Определяем язык по текущей раскладке клавиатуры Windows
            current_lang = state.get_keyboard_language_code()
            update_status(i18n.get_status_text("not_understood", current_lang), "error")
            m.window.show_volume_bar(False)
            m.window.update_volume(0)
        except sr.RequestError as e:
            logger.error(f"Network error with Google Speech Recognition: {e}", exc_info=True)
            # Определяем язык по текущей раскладке клавиатуры Windows
            current_lang = state.get_keyboard_language_code()
            update_status(i18n.get_status_text("network_error", current_lang), "error")
            m.window.show_volume_bar(False)
            m.window.update_volume(0)
        except OSError as e:
            logger.error(f"OSError: {e}", exc_info=True)
            # Определяем язык по текущей раскладке клавиатуры Windows
            current_lang = state.get_keyboard_language_code()
            update_status(i18n.get_status_text("audio_error", current_lang), "error")
            m.window.show_volume_bar(False)
            m.window.update_volume(0)
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))


def view_wget() -> None:
    """
    Запускает главное окно приложения.
    Устанавливает размер, позицию и запускает Qt event loop.
    """
    w.resize(500, 150)
    w.show()
    w.move(GetSystemMetrics(0) - w.size().width(), GetSystemMetrics(1) - conf.window_offset_from_bottom)
    sys.exit(app.exec())

w = subtitle_speach.MainWindow(conf)

l = listner.ListnerManger(state, w)

# Создание иконки для системного трея
def create_tray_icon() -> QSystemTrayIcon:
    """
    Создает иконку в системном трее с контекстным меню.
    
    Returns:
        QSystemTrayIcon: Созданная иконка системного трея
    """
    # Создаем простую иконку (можно заменить на файл .ico позже)
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(70, 130, 180))  # Цвет steelblue
    icon = QIcon(pixmap)
    
    # Альтернатива: можно использовать встроенную иконку
    # icon = QIcon.fromTheme("microphone")  # Если есть системная иконка
    
    tray_icon = QSystemTrayIcon(icon, app)
    tray_icon.setToolTip("Speech Manager")
    
    # Окно настроек (будет создано при первом использовании)
    settings_win = None
    
    def open_settings() -> None:
        """Открывает окно настроек."""
        # Используем функцию с перезагрузкой горячей клавиши
        open_settings_with_reload()
    
    # Создаем контекстное меню
    menu = QMenu()
    
    # Действие "Настройки" - открывается при клике на иконку
    settings_action = QAction("Настройки", w)
    settings_action.triggered.connect(open_settings)
    menu.addAction(settings_action)
    
    menu.addSeparator()
    
    # Действие "Показать/Скрыть"
    show_action = QAction("Показать окно", w)
    hide_action = QAction("Скрыть окно", w)
    
    def toggle_window() -> None:
        """Переключает видимость главного окна."""
        if w.isVisible():
            w.hide()
            # Останавливаем таймер скрытия при скрытии
            w.hide_timer.stop()
            show_action.setVisible(True)
            hide_action.setVisible(False)
        else:
            w.show()
            w.activateWindow()
            # Сбрасываем таймер скрытия при показе
            if w.config and w.config.auto_hide_duration > 0:
                w.schedule_auto_hide()
            show_action.setVisible(False)
            hide_action.setVisible(True)
    
    show_action.triggered.connect(toggle_window)
    hide_action.triggered.connect(toggle_window)
    
    hide_action.setVisible(False)  # Изначально окно видимо
    menu.addAction(show_action)
    menu.addAction(hide_action)
    
    menu.addSeparator()
    
    # Действие "Выход"
    def quit_application() -> None:
        """Завершает работу приложения с корректной очисткой ресурсов."""
        print("Shutting down application...")
        
        # Останавливаем все управляемые потоки
        thread_manager.shutdown(timeout=5.0)
        
        # Удаляем хоткей (библиотека keyboard автоматически завершит поток)
        try:
            if hotkey_handle:
                keyboard.remove_hotkey(hotkey_handle)
        except Exception as e:
            print(f'Error during hotkey cleanup: {e}')
        
        # Выходим из приложения
        QApplication.quit()
    
    def reload_hotkey() -> None:
        """Перезагружает горячую клавишу после изменения настроек."""
        global hotkey_handle
        try:
            # Удаляем старую горячую клавишу
            if hotkey_handle:
                keyboard.remove_hotkey(hotkey_handle)
            
            # Регистрируем новую
            hotkey_handle = keyboard.add_hotkey(conf.hotkey, lambda: process_speech(l))
            logger.info(f"Hotkey reloaded: {conf.hotkey}")
        except Exception as e:
            logger.error(f"Error reloading hotkey: {e}", exc_info=True)
    
    # Сохраняем функцию reload_hotkey в settings_win для вызова после сохранения
    def open_settings_with_reload() -> None:
        """Открывает настройки с последующей перезагрузкой горячей клавиши."""
        nonlocal settings_win
        settings_win = settings_window.SettingsWindow(conf)
        screen = QApplication.desktop().screenGeometry()
        settings_win.move(
            screen.center() - settings_win.rect().center()
        )
        result = settings_win.exec_()
        if result == QDialog.Accepted:
            w.apply_config_settings()
            reload_hotkey()  # ✅ Перезагружаем горячую клавишу после сохранения
    
    quit_action = QAction("Выход", w)
    quit_action.triggered.connect(quit_application)
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    
    # Устанавливаем то же меню для контекстного меню header в MainWindow
    w.context_menu = menu
    
    # Клик по иконке показывает основной интерфейс, двойной клик - настройки
    def on_icon_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Обрабатывает клики по иконке в трее.
        
        Args:
            reason: Причина активации (одинарный клик, двойной клик и т.д.)
        """
        if reason == QSystemTrayIcon.Trigger:
            # Одинарный клик - показываем основное окно
            toggle_window()
        elif reason == QSystemTrayIcon.DoubleClick:
            # Двойной клик - открываем настройки
            open_settings()
    
    tray_icon.activated.connect(on_icon_activated)
    
    # Показываем иконку в трее
    tray_icon.show()
    
    return tray_icon

# Создаем иконку в трее
tray_icon = create_tray_icon()

# Переопределяем закрытие окна - сворачиваем в трей вместо закрытия
def closeEvent(event: QCloseEvent) -> None:
    """
    Обрабатывает событие закрытия окна.
    Сворачивает окно в трей вместо полного закрытия.
    
    Args:
        event: Событие закрытия окна
    """
    event.ignore()
    w.hide()
    tray_icon.showMessage(
        "Speech Manager",
        "Приложение свернуто в системный трей",
        QSystemTrayIcon.Information,
        2000
    )

w.closeEvent = closeEvent

# Запускает слушатель - сохраняем handle для удаления при выходе
# Используем горячую клавишу из конфигурации
hotkey_handle = keyboard.add_hotkey(conf.hotkey, lambda: process_speech(l))
logger.info(f"Hotkey registered: {conf.hotkey}")

# ✅ Qt GUI должен быть в главном потоке, не в worker thread!
# Запускаем view_wget() в главном потоке (он содержит app.exec())
view_wget()
