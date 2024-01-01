import sys

import openai
from PyQt5.Qt import *

import client.gpt as gpt
from threading import Thread
from win32api import GetSystemMetrics

app = QApplication(sys.argv)

LANG_RETURN_COMMANDS = ['gpt подскажи', 'repeat it', 'jupiter puscasu', 'подскажи' ]
LISTNER = ['gpt', 'умничать', 'умный чат',]

def view_wget(w, str, systemMetrics):
    w.resize(800, 500)
    w.show()
    w.move(w.pos().x(), systemMetrics[1]-250)
    w.lables.insertPlainText(str)

def view_wget_asc(w, systemMetrics):
    w.resize(600, 100)
    w.show()
    w.move(w.pos().x(), systemMetrics[1]-250)
    w.lables.insertPlainText("[e[v")


class GptManager():

    def __init__(self, speech_service, config):
        self.speech_service = speech_service
        self.commands = LANG_RETURN_COMMANDS
        self.process = LISTNER
        self.openai = openai
        self.openai.api_key = config.GPT_KEY

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

    def run(self, str, state):
        w = AscWindow()
        tw = Thread(target=view_wget_asc(w, state.systemMetrics), args=())
        tw.start()

    def process_to_run(self, str):
        result = ""
        try:
            result = self.getByString(str, )
        except:
            print(str, ": error")
        # try:
        #     w = answer.AnswerWindow()
        #     tw = Thread(target=view_wget(w, result), args=())
        #     tw.start()
        # except:
        #     print(str, ": error")
        print(result)

    def getByString(self, str, api_key):
        openai.api_key = api_key
        print(str, openai)
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=str,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response['choices'][0].text

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.line = QFrame(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.line)
        main_layout.addStretch()
        self.setWindowFlags(Qt.FramelessWindowHint)


class AnswerWindow(QMainWindow):  # QMainWindow  -QWidget
    def __init__(self):
        super(AnswerWindow, self).__init__()
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.widget = Widget(self)
        lbl = QLabel('', self, alignment=Qt.AlignTop)
        lbl.setStyleSheet("""
            QLabel {
                font-family: 'Consolas'; 
                color: green; 
                font-size: 30px;
            }
        """)
        self.lable = lbl
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""MainWindow {background-color: rgba(255, 255, 255,    20);}""")

        self.setWindowFlags(self.windowFlags() |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self.centralwidget)
        layout.addWidget(self.widget)
        layout.addWidget(lbl)
        layout.addStretch()



    def mousePressEvent(self, event):
        self.old_Pos    = event.globalPos()
        self.old_width  = self.width()
        self.old_height = self.height()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            delta = QPoint (event.globalPos() - self.old_Pos)
            if (self.old_Pos.x() > self.x() + self.old_width - 20) or \
               (self.old_Pos.y() > self.y() + self.old_height - 20):
                w = self.old_width+delta.x()  if self.old_width+delta.x()  > 900 else 500
                h = self.old_height+delta.y() if self.old_height+delta.y() > 400 else 400
                self.setFixedSize(w, h)
            else:
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_Pos = event.globalPos()


class AscWindow(QMainWindow):  # QMainWindow  -QWidgetimport sys
    def __init__(self):
        super(AscWindow, self).__init__()
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.widget = Widget(self)
        lbl = QLabel('', self, alignment=Qt.AlignTop)
        lbl.setStyleSheet("""
            QLabel {
                font-family: 'Consolas'; 
                color: green; 
                font-size: 30px;
            }
        """)
        self.lable = lbl
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""MainWindow {background-color: rgba(255, 255, 255,    20);}""")

        self.setWindowFlags(self.windowFlags() |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self.centralwidget)
        layout.addWidget(self.widget)
        layout.addWidget(lbl)
        layout.addStretch()



    def mousePressEvent(self, event):
        self.old_Pos    = event.globalPos()
        self.old_width  = self.width()
        self.old_height = self.height()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            delta = QPoint (event.globalPos() - self.old_Pos)
            if (self.old_Pos.x() > self.x() + self.old_width - 20) or \
               (self.old_Pos.y() > self.y() + self.old_height - 20):
                w = self.old_width+delta.x()  if self.old_width+delta.x()  > 500 else 500
                h = self.old_height+delta.y() if self.old_height+delta.y() > 400 else 400
                self.setFixedSize(w, h)
            else:
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_Pos = event.globalPos()