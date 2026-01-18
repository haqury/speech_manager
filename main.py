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

import subtitle_speach
import dialog_speach
import settings_window

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from threading import Thread

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
audio_data = None
audio_data_output = None

# Флаг для завершения потоков
shutdown_flag = False


def manager_proc(w):
    print('manager_proc: start')
    global state
    global shutdown_flag
    m = manager.Managers(w)
    curr_manager = m
    while not shutdown_flag:
        if state.listner != 'manager':
            time.sleep(3)
            continue

        with sr.Microphone() as source:
            # try:
            try:
                curr_manager.start()
            except:
                print('not start')
            # if curr_manager == m:
            #     speech_service.list_file(PATH_FILE_SPEECH_FIRST)
            # speech_service.speech('выберите менеджера', 'ru')

            ad = r.listen(source, phrase_time_limit=6)
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
    global audio_data
    global shutdown_flag
    while not shutdown_flag:
        if audio_data is None:
            time.sleep(0.5)
            continue

        if state.listner != 'write':
            time.sleep(0.5)
            continue

        try:

            ad = audio_data
            audio_data = None
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

    with sr.Microphone() as source:
        try:
            m.window.statelbl.setText("speech-to-text on")
            m.pocessAudio(r.listen(source, phrase_time_limit=8))
            m.window.statelbl.setText("speech-to-text off")
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

    # dw.resize(500, 150)
    # dw.show()
    # dw.move(GetSystemMetrics(0)-w.size().width(), GetSystemMetrics(1)-400)

    # objectName = keybaord.VirtualKeyboard()
    # objectName.engine()
    # objectName.start()

    sys.exit(app.exec())

w = subtitle_speach.MainWindow()
# dw = dialog_speach.MainWindow()
# w = chat.ChatApp()

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
        settings_win.exec_()
    
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
            show_action.setVisible(True)
            hide_action.setVisible(False)
        else:
            w.show()
            w.activateWindow()
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
        global shutdown_flag
        shutdown_flag = True
        # Удаляем хоткей (библиотека keyboard автоматически завершит поток)
        try:
            # Просто завершаем приложение - keyboard сам закроет хоткеи
            pass
        except:
            pass
        # Выходим из приложения
        QApplication.quit()
    
    quit_action = QAction("Выход", w)
    quit_action.triggered.connect(quit_application)
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    
    # Клик по иконке открывает настройки, двойной клик - показывает/скрывает окно
    def on_icon_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            # Одинарный клик - открываем настройки
            open_settings()
        elif reason == QSystemTrayIcon.DoubleClick:
            # Двойной клик - показываем/скрываем окно
            toggle_window()
    
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

th = Thread(target=write_proc, args=(w,))
th.start()


tm = Thread(target=manager_proc, args=(w,))
tm.start()

tw = Thread(target=view_wget(), args=())
tw.start()

external_variable = 0
