import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import *

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