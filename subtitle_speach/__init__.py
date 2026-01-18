from PyQt5.Qt import *
from PyQt5.QtCore import pyqtSlot
import pyperclip as pc
import numpy as np


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
    def __init__(self, config=None):
        super(MainWindow, self).__init__()
        self.config = config
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.message_fields = []
        
        # Таймер для автоматического скрытия
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.hide)
        self.hide_timer.setSingleShot(True)

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
        # Делаем statelbl кликабельным для сворачивания
        self.statelbl.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.statelbl)

        self.statelbl.setText("speech-to-text off")
        
        # Обработчик клика на statelbl для сворачивания (левый клик) и контекстного меню (правый клик)
        self.context_menu = None  # Будет установлено из main.py
        
        def on_statelbl_clicked(event):
            if event.button() == Qt.LeftButton:
                # Левый клик - сворачивание
                self.hide()
            elif event.button() == Qt.RightButton:
                # Правый клик - контекстное меню
                if self.context_menu:
                    self.context_menu.exec_(event.globalPos())
        self.statelbl.mousePressEvent = on_statelbl_clicked

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
        
        # Применяем настройки при инициализации
        self.apply_config_settings()

    def addAnswer(self, str):
        lbl = self.getNextLabel()
        lbl.setText(str)
        self.schedule_auto_hide()
    
    def schedule_auto_hide(self):
        """Запускает таймер автоматического скрытия на основе настроек"""
        if not self.config:
            return
        
        if self.config.auto_hide_duration > 0:
            # Используем QMetaObject.invokeMethod для вызова из главного потока Qt
            # Это безопасно работает даже если вызывается из другого потока
            duration_ms = int(self.config.auto_hide_duration * 1000)
            QMetaObject.invokeMethod(self, "_start_hide_timer", Qt.QueuedConnection, Q_ARG(int, duration_ms))
    
    @pyqtSlot(int)
    def _start_hide_timer(self, duration_ms):
        """Запускает таймер - вызывается из главного потока Qt"""
        # Останавливаем предыдущий таймер если он запущен
        self.hide_timer.stop()
        # Запускаем новый таймер
        self.hide_timer.start(duration_ms)
    
    def apply_config_settings(self):
        """Применяет настройки из config к окну"""
        if not self.config:
            return
        
        # Применяем прозрачность окна
        self.setWindowOpacity(self.config.opacity)
        
        # Применяем размер шрифта ко всем лейблам
        font_size = self.config.font_size
        font_size_str = f"{font_size}px"
        
        # Обновляем стиль statelbl
        self.statelbl.setStyleSheet(f"""
            QLabel {{
                font-family: 'Consolas';
                background-color: rgba(0, 0, 0,  40);
                color: red;
                font-size: {font_size_str};
            }}
        """)
        
        # Обновляем стиль всех labels с сообщениями
        for lbl in self.labels:
            lbl.setStyleSheet(f"""
                QLabel {{
                    font-family: 'Consolas';
                    background-color: rgba(0, 0, 0,  40);
                    color: green;
                    font-size: {font_size_str};
                }}
            """)
        
        # Управляем количеством labels на основе max_messages
        # Если max_messages меньше текущего количества, удаляем лишние
        # Если больше - добавляем новые (максимум до разумного предела, например 10)
        current_count = len(self.labels)
        target_count = min(max(self.config.max_messages, 1), 10)  # От 1 до 10
        
        if target_count < current_count:
            # Удаляем лишние (но сохраняем минимум структуру)
            pass  # Оставляем как есть, просто не используем лишние
        elif target_count > current_count:
            # Добавляем новые labels
            layout = self.centralwidget.layout()
            for i in range(current_count, target_count):
                new_lbl = MessageLabel(self)
                new_lbl.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Consolas';
                        background-color: rgba(0, 0, 0,  40);
                        color: green;
                        font-size: {font_size_str};
                    }}
                """)
                # Вставляем перед stretch
                layout.insertWidget(layout.count() - 1, new_lbl)
                self.labels.append(new_lbl)

    def getNextLabel(self) -> QLabel:
        # Определяем сколько labels нужно использовать на основе max_messages
        max_labels = min(len(self.labels), self.config.max_messages if self.config else len(self.labels))
        labels_to_use = self.labels[:max_labels]
        
        # Ищем пустой label
        for a in labels_to_use:
            if not a.text():
                return a

        # Если все заполнены, сдвигаем вверх
        i = 0
        while i < len(labels_to_use):
            if i + 1 == len(labels_to_use):
                return labels_to_use[i]
            labels_to_use[i].setText(labels_to_use[i + 1].text())
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
