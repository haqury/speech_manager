import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import *
import pyperclip as pc

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.line = QFrame(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.line)
        main_layout.addStretch()
        self.setWindowFlags(Qt.FramelessWindowHint)

class MessageLabel(QLabel):
    def mousePressEvent(self, event):
        pc.copy(self.text())


class MainWindow(QMainWindow):  # QMainWindow  -QWidget
    def __init__(self):
        super(MainWindow, self).__init__()
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.message_fields = []

        self.widget = Widget(self)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""MainWindow {background-color: rgba(0, 0, 0,    20);}""")

        self.setWindowFlags(self.windowFlags() |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self.centralwidget)
        layout.addWidget(self.widget)
        self.lables = []
        lbl = QLabel()
        lbl.setStyleSheet("""
                QLabel {
                    font-family: 'Consolas';
                    color: green;
                    font-size: 30px;

                }
            """)

        self.lable = lbl
        layout.addWidget(lbl)

        # i = 0
        # while i < 3:
        #     lbl = MessageLabel()
        #     lbl.setStyleSheet("""
        #             QLabel {
        #                 font-family: 'Consolas';
        #                 color: green;
        #                 font-size: 30px;
        #                 background-color: rgba(0, 0, 0,    20);
        #             }
        #         """)
        #
        #     self.message_fields.append(lbl)
        #     layout.addWidget(lbl)
        #     i = i + 1

        layout.addStretch()


    # def addAnswer(self, str):
        # lbl = QPlainTextEdit()
        # lbl.setStyleSheet("""
        #     QPlainTextEdit {
        #         font-family: 'Consolas';
        #         color: green;
        #         font-size: 30px;
        #
        #     }
        # """)
        #
        # layout = QVBoxLayout(self.centralwidget)
        # layout.addWidget(lbl)
        # layout.addStretch()
        # for l in self.lables:
        #     # if l.toPlainText() == '':
        #     l.insertPlainText(str)


        # lbl = self.getNextLabel()
        # lbl.setText(str)

    def getNextLabel(self) -> MessageLabel:
        for a in self.message_fields:
            if not a.text():
                return a
        for i, a in self.message_fields:
            if not self.message_fields[i + 1]:
                return a
            self.message_fields[i] = self.message_fields[i+1]




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
    def mouseDoubleClickEvent(self, event):
        pc.copy(self.lable.text())