import sys

from PyQt5.QtWidgets import QApplication

from speach_manager import speech_service
import speach_manager.client.gpt as gpt
from threading import Thread
from win32api import GetSystemMetrics
import speach_manager.manager.gpt.answer

app = QApplication(sys.argv)

LANG_RETURN_COMMANDS = ['gpt подскажи', 'repeat it', 'jupiter puscasu', 'подскажи' ]
LISTNER = ['gpt', 'умничать', 'умный чат',]

def view_wget(w, str):
    w.resize(800, 500)
    w.show()
    w.move(w.pos().x(), GetSystemMetrics(1)-250)
    w.lables.insertPlainText(str)
def view_wget_asc(w):
    w.resize(600, 100)
    w.show()
    w.move(w.pos().x(), GetSystemMetrics(1)-250)
    w.lables.insertPlainText("[e[v")

class GptManager():

    def __init__(self):
        self.speech_service = speech_service.SpeechService()
        self.commands = LANG_RETURN_COMMANDS
        self.process = LISTNER

    def start(self):
        self.speech_service.speech('да', self.speech_service.LANG_RUS)

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False
    def is_spec_proc(self, name) -> bool:
        for c in self.process:
            if c.find(name) != -1:
                return True

        return False

    def run(self, str):
        w = answer.AscWindow()
        tw = Thread(target=view_wget_asc(w), args=())
        tw.start()

    def process_to_run(self, str):
        result = ""
        try:
            result = gpt.getByString(str)
        except:
            print(str, ": error")
        # try:
        #     w = answer.AnswerWindow()
        #     tw = Thread(target=view_wget(w, result), args=())
        #     tw.start()
        # except:
        #     print(str, ": error")
        print(result)
