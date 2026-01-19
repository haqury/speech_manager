#!/usr/bin/env python3
import sys
import time
from win32api import GetSystemMetrics
import keyboard
from pynput import keyboard as hotkeyPackage

import config

import state as s
import error
import listner
import manager
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
    ThreadSafeAudioQueue,
    WorkerLoop,
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
audio_queue = ThreadSafeAudioQueue(maxsize=10)

# Печатаем информацию о режиме многопоточности
print_threading_info()


def manager_proc(w):
    print('manager_proc: start')
    global state
    m = manager.Managers(w)
    curr_manager = m
    while not thread_manager.is_shutting_down():
        if state.listner != 'manager':
            time.sleep(3)
            continue

        # Используем MicrophoneStream вместо sr.Microphone (PyAudio заменен на SoundDevice)
        with MicrophoneStream(
            energy_threshold=conf.energy_threshold,
            pause_threshold=conf.pause_threshold
        ) as source:
            try:
                curr_manager.start()
            except Exception as e:
                print(f'Manager start failed: {e}')

            ad = source.listen(phrase_time_limit=6)
            m.write('record')
            result = r.recognize_google(ad, language=state.get_keyboard_language(), show_all=True)
            str = l.get_string(speach_resul=result)
            if not str:
                continue
            m.write(str)

            if l.is_command_write(str):
                curr_manager = m
                state.listner = 'write'
                continue

            if curr_manager == m:
                curr_manager = m.spec(str) or m
                continue

            curr_manager.process_to_run(str)

        # except sr.UnknownValueError:
        #     logger.log("Google Speech Recognition could not understand audio")
        # except sr.RequestError as e:
        #     logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
        # except OSError as e:
        #     logger.log("OSError service; {0}".format(e))
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))


def write_proc(w):
    print('write_proc: start')
    global state
    while not thread_manager.is_shutting_down():
        # Получаем аудио из очереди (thread-safe)
        ad = audio_queue.get(block=True, timeout=0.5)
        
        if ad is None:
            continue

        if state.listner != 'write':
            continue

        try:
            result = r.recognize_google(ad, language=state.get_keyboard_language(), show_all=True)

            str = l.get_string(speach_resul=result)
            if not str:
                continue

            c = l.is_commands(str)
            if c:
                state.listner = 'manager'

            c = l.is_commands_state(str)
            if c:
                l.get_command_secification(str)

            pr = Thread(target=l.process, args=(result,))
            pr.start()

        except sr.UnknownValueError:
            logger.log("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
        except OSError as e:
            logger.log("OSError service; {0}".format(e))
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))
        #     print()

def listed():
    print('listed write')
    if state.listner != 'write':
        return
    tll = Thread(target=list, args=())
    tll.start()
    time.sleep(2.8)

def list(m):
    global audio_data

    # Callback функции для синхронизации UI с состоянием записи
    def on_speech_start():
        """Вызывается когда начинается реальная запись речи"""
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
    
    def on_speech_end():
        """Вызывается когда заканчивается запись речи"""
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
            
            m.pocessAudio(source.listen(phrase_time_limit=8))
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


def view_wget():
    w.resize(500, 150)
    w.show()
    w.move(GetSystemMetrics(0) - w.size().width(), GetSystemMetrics(1) - 400)
    sys.exit(app.exec())

w = subtitle_speach.MainWindow(conf)

l = listner.ListnerManger(state, w)

# Создание иконки для системного трея
def create_tray_icon():
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
    
    def open_settings():
        nonlocal settings_win
        # Создаем новое окно настроек каждый раз (QDialog)
        settings_win = settings_window.SettingsWindow(conf)
        # Центрируем окно на экране
        screen = QApplication.desktop().screenGeometry()
        settings_win.move(
            screen.center() - settings_win.rect().center()
        )
        # exec_() делает окно модальным и блокирует до закрытия
        result = settings_win.exec_()
        # После сохранения настроек применяем их к окну
        if result == QDialog.Accepted:
            w.apply_config_settings()
    
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
    
    def toggle_window():
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
    def quit_application():
        print("Shutting down application...")
        
        # Останавливаем все управляемые потоки
        thread_manager.shutdown(timeout=5.0)
        
        # Удаляем хоткей (библиотека keyboard автоматически завершит поток)
        try:
            keyboard.remove_hotkey(hotkey_handle)
        except Exception as e:
            print(f'Error during hotkey cleanup: {e}')
        
        # Выходим из приложения
        QApplication.quit()
    
    quit_action = QAction("Выход", w)
    quit_action.triggered.connect(quit_application)
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    
    # Устанавливаем то же меню для контекстного меню header в MainWindow
    w.context_menu = menu
    
    # Клик по иконке показывает основной интерфейс, двойной клик - настройки
    def on_icon_activated(reason):
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
def closeEvent(event):
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
hotkey_handle = keyboard.add_hotkey('ctrl+shift+win+f5', lambda: list(l))

# Создаем управляемые потоки через ThreadManager (Python 3.14 ready!)
thread_manager.create_worker(
    target=write_proc,
    args=(w,),
    name="WriteProcessor",
    daemon=True
)

thread_manager.create_worker(
    target=manager_proc,
    args=(w,),
    name="ManagerProcessor",
    daemon=True
)

# ✅ Qt GUI должен быть в главном потоке, не в worker thread!
# Запускаем view_wget() в главном потоке (он содержит app.exec())
view_wget()
