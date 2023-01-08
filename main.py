#!/usr/bin/env python3
import sys
import time

from win32api import GetSystemMetrics

import config
import state
import error
import listner
import speech_recognition as sr
from pythonProject import subtitle_speach

from PyQt5.Qt import *
from threading import Thread

r = sr.Recognizer()

conf = config.Config
s = state.State(conf)

app = QApplication(sys.argv)


logger = error.Logger()
audio_data = None

def proc():
    global audio_data
    while 1:
        if audio_data is None:
            time.sleep(1)
            continue

        try:
            result = r.recognize_google(audio_data, language=state.get_keyboard_language(), show_all=True)
            l.process(result)
            audio_data = None

        except sr.UnknownValueError:
            logger.log("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
        except OSError as e:
            logger.log("OSError service; {0}".format(e))
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))

def listed():
    global audio_data

    with sr.Microphone() as source:
        while 1:
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
l = listner.ListnerManger(s, w)
th = Thread(target=proc, args=())
th.start()
tl = Thread(target=listed, args=())
tl.start()
tw = Thread(target=view_wget(), args=())
tw.start()
