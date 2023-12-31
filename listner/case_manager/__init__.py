import pyperclip as pc

from PyQt5.Qt import *
import numpy as np

SNAKE_CASE = ['snake', 'make', 'снейк', 'smokies']
CAMEL_CASE = ['camel', 'como', 'кому', 'хаббл', 'kamo']
DEFAULT_CASE = ['default', 'the fault', 'the fall', 'дефолт_кейс', 'стандарт_кейс']
IS_UP = ['is up', 'из opt', 'is app', 'is apt']



class CaseManager:
    def __init__(self, listner_manager):
        self.commands = IS_UP + SNAKE_CASE + CAMEL_CASE + DEFAULT_CASE
        self.listner_manager = listner_manager

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self, str):
        for case in SNAKE_CASE:
            if str.find(case) != -1:
                self.change_case(2)
                return 2

        for case in CAMEL_CASE:
            if str.find(case) != -1:
                self.change_case(1)
                return 1

        for case in DEFAULT_CASE:
            if str.find(case) != -1:
                self.change_case(0)
                return 0

        if str.find('is up') != -1:
            if str.find('true') != -1 \
                    or str.find('through') != -1 \
                    or str.find('.ru')  != -1 \
                    or str.find('room')  != -1 \
                    or str.find('ton')  != -1:
                self.change_uper(True)
            else:
                self.change_uper(False)

    def change_case(self, type):
        self.listner_manager.state.case = type
        self.listner_manager.last_rebuld()

    def change_uper(self, type):
        print('upper case', type)
        self.listner_manager.state.is_up = type
        self.listner_manager.last_rebuld()

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.line = QFrame(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.line)
        main_layout.addStretch()
        self.setWindowFlags(self.windowFlags())

class MessageLabel(QLabel):
    def mousePressEvent(self, event):
        if self.text():
            pc.copy(self.text())

    def mouseDoubleClickEvent(self, event):
        if self.text():
            pc.copy(self.text())
            self.setText('')


class MainWindow(QMainWindow):  # QMainWindow  -QWidget
    def __init__(self):
        super(MainWindow, self).__init__()
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.message_fields = []

        self.widget = Widget(self)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("""MainWindow {background-color: rgba(0, 0, 0,    4);}""")

        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self.centralwidget)
        layout.addWidget(self.widget)

        self.statelbl = QLabel(self)
        self.statelbl.setStyleSheet("""
                    QLabel {
                        font-family: 'Consolas';
                        background-color: rgba(0, 0, 0,  40);
                        color: red;
                        font-size: 30px;

                    }
                """)
        layout.addWidget(self.statelbl)

        self.statelbl.setText("speech-to-text off")

        self.labels = [MessageLabel(self) for i in range(3)]
        for i, lbl in enumerate(self.labels):
            lbl.setStyleSheet("""
                    QLabel {
                        font-family: 'Consolas';
                        background-color: rgba(0, 0, 0,  40);
                        color: green;
                        font-size: 30px;

                    }
                """)
            layout.addWidget(lbl)

        layout.addStretch()

        self.setWindowFlags(Qt.Tool |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)

    def addAnswer(self, str):
        lbl = self.getNextLabel()
        lbl.setText(str)

    def getNextLabel(self) -> QLabel:
        for a in self.labels:
            if not a.text():
                return a

        i = 0
        while i < len(self.labels):
            if i + 1 == len(self.labels):
                return self.labels[i]
            self.labels[i].setText(self.labels[i + 1].text())
            i += 1

    def mousePressEvent(self, event):
        self.old_Pos = event.globalPos()
        self.old_width = self.width()
        self.old_height = self.height()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            delta = QPoint(event.globalPos() - self.old_Pos)
            if (self.old_Pos.x() > self.x() + self.old_width - 20) or \
                    (self.old_Pos.y() > self.y() + self.old_height - 20):
                w = self.old_width + delta.x() if self.old_width + delta.x() > 500 else 500
                h = self.old_height + delta.y() if self.old_height + delta.y() > 400 else 400
                self.setFixedSize(w, h)
            else:
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_Pos = event.globalPos()
