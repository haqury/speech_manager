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
from typing import Optional
from win32api import GetSystemMetrics
import keyboard
from pynput import keyboard as hotkeyPackage

import config

import state as s
import error
import listner
import speech_recognition as sr
from audio_recorder import MicrophoneStream

import subtitle_speach
import settings_window

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from threading import Thread

# Modern threading для Python 3.14+
from threading_manager import (
    ThreadManager,
    print_threading_info
)


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

logger = error.Logger()

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

    # Callback функции для синхронизации UI с состоянием записи
    def on_speech_start() -> None:
        """Вызывается когда начинается реальная запись речи."""
        try:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            # Используем invokeMethod с Q_ARG для безопасного обновления UI из другого потока
            QMetaObject.invokeMethod(
                m.window.statelbl,
                "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "speech-to-text on")
            )
        except Exception as e:
            print(f"Error updating UI on speech start: {e}")
    
    def on_speech_end() -> None:
        """Вызывается когда заканчивается запись речи."""
        try:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                m.window.statelbl,
                "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "speech-to-text off")
            )
        except Exception as e:
            print(f"Error updating UI on speech end: {e}")

    # Используем MicrophoneStream вместо sr.Microphone (PyAudio заменен на SoundDevice)
    with MicrophoneStream(
        energy_threshold=m.window.config.energy_threshold if m.window.config else 300,
        pause_threshold=m.window.config.pause_threshold if m.window.config else 0.8,
        on_speech_start=on_speech_start,
        on_speech_end=on_speech_end
    ) as source:
        try:
            # Показываем окно при активации прослушивания
            if not m.window.isVisible():
                m.window.show()
                m.window.activateWindow()
                m.window.raise_()
            
            m.window.statelbl.setText("Listening...")
            # Сбрасываем таймер скрытия при активации
            if m.window.config and m.window.config.auto_hide_duration > 0:
                m.window.hide_timer.stop()
            
            # Слушаем и распознаем речь
            audio_data = source.listen(phrase_time_limit=conf.phrase_time_limit)
            
            try:
                # Распознаем через Google Speech Recognition
                result = r.recognize_google(audio_data, language=state.get_keyboard_language(), show_all=True)
                
                # Обрабатываем результат
                m.process(result)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition: {e}")
            except Exception as e:
                print(f"Error processing speech: {e}")
            
            m.window.statelbl.setText("speech-to-text off")
            
            # Запускаем таймер скрытия после окончания прослушивания
            if m.window.config and m.window.config.auto_hide_duration > 0:
                m.window.schedule_auto_hide()
        except sr.UnknownValueError:
            logger.log("Google Speech Recognition could not understand audio")
            m.window.statelbl.setText("speech-to-text off")
        except sr.RequestError as e:
            logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
            m.window.statelbl.setText("speech-to-text off")
        except OSError as e:
            logger.log("OSError service; {0}".format(e))
            m.window.statelbl.setText("speech-to-text off")
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
            print(f"Hotkey reloaded: {conf.hotkey}")
        except Exception as e:
            print(f"Error reloading hotkey: {e}")
    
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
print(f"Hotkey registered: {conf.hotkey}")

# ✅ Qt GUI должен быть в главном потоке, не в worker thread!
# Запускаем view_wget() в главном потоке (он содержит app.exec())
view_wget()
