#!/usr/bin/env python3
import sys
import time
from win32api import GetSystemMetrics

import config

import speach_manager.speech_service
import state as s
import error
import listner
import manager
import speech_recognition as sr

# import manager

import subtitle_speach

from PyQt5.Qt import *
from threading import Thread

from speach_manager import chat

r = sr.Recognizer()

conf = config.Config
state = s.State(conf)

app = QApplication(sys.argv)


logger = error.Logger()
audio_data = None
audio_data_output = None


def manager_proc(w):
    print('manager_proc: start')
    global state
    m = manager.Managers(w)
    curr_manager = m
    while 1:
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
                #     speach_manager.speech_service.list_file(PATH_FILE_SPEECH_FIRST)
                # speach_manager.speech_service.speech('выберите менеджера', 'ru')

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


def write_proc():
    print('write_proc: start')
    global state
    global audio_data
    while 1:
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
        while 1:
            if state.listner != 'write':
                time.sleep(0.5)
                continue
            tll = Thread(target=list, args=())
            tll.start()
            time.sleep(2.8)

def list():
    global audio_data

    with sr.Microphone() as source:
        try:
            audio_data = r.listen(source, phrase_time_limit=3)
        except sr.UnknownValueError:
            logger.log("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
        except OSError as e:
            logger.log("OSError service; {0}".format(e))
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))


def view_wget():
    w.resize(800, 150)
    w.show()
    w.move(w.pos().x(), GetSystemMetrics(1)-250)
    sys.exit(app.exec())

w = subtitle_speach.MainWindow()
# w = chat.ChatApp()


l = listner.ListnerManger(state, w)
th = Thread(target=write_proc, args=())
th.start()
tl = Thread(target=listed, args=())
tl.start()

tm = Thread(target=manager_proc, args=(w,))
tm.start()


tw = Thread(target=view_wget(), args=())
tw.start()