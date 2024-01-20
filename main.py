#!/usr/bin/env python3
import sys
import time

import CaseManager
import ConfigManager
import SpeachToTextWidget, DearWidgetTemplate
import keyboard

import speech_service
import config
import gpt

import state as s
import error
import listner
import speech_recognition as sr

from PyQt5.Qt import *
from threading import Thread

from dotenv import load_dotenv

load_dotenv()
conf = config.Config()
state = s.State(conf)

app = QApplication(sys.argv)

logger = error.Logger()
audio_data = None
audio_data_output = None

def list(m):
    r = sr.Recognizer()
    global audio_data

    with sr.Microphone() as source:
        try:
            m.window.statelbl.setText("speech-to-text on")
            m.pocessAudio(r.listen(source, phrase_time_limit=5))
            m.window.statelbl.setText("speech-to-text off")
        except sr.UnknownValueError:
            logger.log("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
        except OSError as e:
            logger.log("OSError service; {0}".format(e))
        # except TypeError as e:
        #     logger.log("TypeError service; {0}".format(e))



def view_wget():
    app = QApplication(sys.argv)

    sys.exit(app.exec_())

main_window = DearWidgetTemplate.App(state)

speach = SpeachToTextWidget.SpeachToTextWidget()

speach.resize(500, 150)
speach.show()
speach.move(500, 400)

main_window.widget_manager.add_widget(3, speach)

main_window.show_widget(3)

ss = speech_service.SpeechService()
l = listner.ListnerManger(state, main_window)
managers = [
            CaseManager.CaseManager(l),
            ss,
            ConfigManager.ConfigManager(l),
            gpt.GptManager(ss, l.state.Config)
        ]
l.setManagers(managers)

# Запускает слушатель
keyboard.add_hotkey('ctrl+shift+win+f5', lambda: list(l))

tw = Thread(target=view_wget(), args=())
tw.start()

external_variable = 0
