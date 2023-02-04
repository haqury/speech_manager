import sys
from PyQt5.Qt import *
import pyperclip as pc

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat App")

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.layout = Q(self.widget)

        self.message_field = QTextEdit(self.widget)
        self.message_field.setReadOnly(True)
        self.layout.addWidget(self.message_field)

        self.entry_field = QLineEdit(self.widget)
        self.layout.addWidget(self.entry_field)

        self.send_button = QPushButton("Send", self.widget)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

    def send_message(self):
        message = self.entry_field.text()
        self.entry_field.clear()
        self.message_field.append(message)

    def addAnswer(self, str):
        self.getNextLabel()
        self.layout.addWidget(self.message_field)


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