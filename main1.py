import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

label = QLabel("This is a label")
layout.addWidget(label)

button = QPushButton("Click me!")
layout.addWidget(button)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())