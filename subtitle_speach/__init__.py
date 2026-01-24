from typing import Optional

from PyQt5.Qt import *
from PyQt5.QtCore import pyqtSlot
import pyperclip as pc


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
    """Main window for displaying recognized speech."""
    
    def __init__(self, config: Optional['config.Config'] = None) -> None:
        """
        Initialize main window.
        
        Args:
            config: Application configuration
        """
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
                        color: #888888;
                        font-size: 30px;

                    }
                """)
        # Делаем statelbl кликабельным для сворачивания
        self.statelbl.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.statelbl)

        # Импортируем i18n для локализации
        # Используем текущую раскладку клавиатуры Windows
        try:
            import i18n
            import state as s
            import config as config_module
            
            # Создаем временный State для определения раскладки
            temp_config = self.config if self.config else config_module.Config()
            temp_state = s.State(temp_config)
            current_lang = temp_state.get_keyboard_language_code()
            
            self.statelbl.setText(i18n.get_status_text("ready", current_lang))
        except (ImportError, Exception):
            # Fallback если i18n не доступен
            self.statelbl.setText("⏸️ Ready...")
        
        # Визуализатор громкости (progress bar)
        self.volume_bar = QProgressBar(self)
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)
        self.volume_bar.setTextVisible(False)
        self.volume_bar.setFixedHeight(8)
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(40, 40, 40, 100);
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FF00,
                    stop:0.5 #FFFF00,
                    stop:1 #FF0000
                );
                border-radius: 4px;
            }
        """)
        self.volume_bar.setVisible(False)  # Скрыт по умолчанию
        layout.addWidget(self.volume_bar)
        
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

    def addAnswer(self, text: str):
        """
        Добавляет текст в следующее доступное поле сообщения.
        Обрезает текст до максимальной длины, если настроено.
        
        Args:
            text: Текст для отображения
        """
        lbl = self.getNextLabel()
        
        # Обрезаем текст до максимальной длины, если настроено
        if self.config and hasattr(self.config, 'max_message_length'):
            max_length = self.config.max_message_length
            if max_length > 0 and len(text) > max_length:
                # Обрезаем и добавляем индикатор обрезки
                text = text[:max_length - 3] + "..."
        
        lbl.setText(text)
        # Автоматически подстраиваем ширину окна под содержимое
        self.adjust_window_width()
        self.schedule_auto_hide()
    
    def update_volume(self, volume: int) -> None:
        """
        Обновляет визуализатор громкости.
        
        Args:
            volume: Уровень громкости (0-100)
        """
        try:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                self.volume_bar,
                "setValue",
                Qt.QueuedConnection,
                Q_ARG(int, volume)
            )
        except Exception as e:
            pass  # Игнорируем ошибки визуализации
    
    def show_volume_bar(self, show: bool = True) -> None:
        """
        Показывает/скрывает визуализатор громкости.
        
        Args:
            show: True для показа, False для скрытия
        """
        try:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                self.volume_bar,
                "setVisible",
                Qt.QueuedConnection,
                Q_ARG(bool, show)
            )
        except Exception as e:
            pass
    
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
    
    def adjust_window_width(self):
        """
        Автоматически подстраивает ширину окна под длину самого длинного текста.
        """
        if not self.config:
            return
        
        # Получаем шрифт из одного из лейблов
        font = self.statelbl.font()
        font.setPointSize(self.config.font_size)
        font_metrics = QFontMetrics(font)
        
        # Находим самую длинную строку среди всех лейблов
        max_width = 0
        
        # Проверяем statelbl
        statelbl_text = self.statelbl.text()
        if statelbl_text:
            # Используем boundingRect для получения ширины текста
            text_rect = font_metrics.boundingRect(statelbl_text)
            text_width = text_rect.width()
            max_width = max(max_width, text_width)
        
        # Проверяем все labels с сообщениями
        for lbl in self.labels:
            label_text = lbl.text()
            if label_text:
                # Используем boundingRect для получения ширины текста
                text_rect = font_metrics.boundingRect(label_text)
                text_width = text_rect.width()
                max_width = max(max_width, text_width)
        
        # Если есть текст, устанавливаем ширину с учетом отступов
        if max_width > 0:
            # Добавляем отступы: 40px слева и справа + небольшой запас
            padding = 80
            min_width = 300  # Минимальная ширина окна
            optimal_width = max(min_width, max_width + padding)
            
            # Ограничиваем максимальной шириной экрана (с небольшим запасом)
            screen_width = QApplication.desktop().screenGeometry().width()
            max_window_width = int(screen_width * 0.9)  # 90% ширины экрана
            optimal_width = min(optimal_width, max_window_width)
            
            # Устанавливаем новую ширину, сохраняя текущую высоту
            current_height = self.height()
            self.resize(optimal_width, current_height)
    
    def apply_config_settings(self):
        """Применяет настройки из config к окну"""
        if not self.config:
            return
        
        # Применяем прозрачность окна
        self.setWindowOpacity(self.config.opacity)
        
        # Применяем размер шрифта ко всем лейблам
        font_size = self.config.font_size
        font_size_str = f"{font_size}px"
        
        # Обновляем стиль statelbl (используем серый цвет для 'off')
        from subtitle_speach.status_colors import get_status_style
        self.statelbl.setStyleSheet(get_status_style('off', font_size))
        
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
        
        # ✅ FIX: Управляем количеством labels с cleanup старых
        current_count = len(self.labels)
        target_count = min(max(self.config.max_messages, 1), 100)  # От 1 до 100 (было 10)
        
        if target_count < current_count:
            # ✅ FIX: Удаляем лишние labels для предотвращения утечки памяти
            self._cleanup_excess_labels(target_count)
        elif target_count > current_count:
            # Добавляем новые labels (но не больше разумного предела)
            layout = self.centralwidget.layout()
            for i in range(current_count, min(target_count, 100)):
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
        
        # Подстраиваем ширину окна после изменения настроек
        self.adjust_window_width()
    
    def _cleanup_excess_labels(self, target_count: int):
        """
        ✅ FIX: Удаляет лишние labels для предотвращения утечки памяти.
        
        Args:
            target_count: Желаемое количество labels
        """
        while len(self.labels) > target_count:
            # Удаляем последний label
            old_label = self.labels.pop()
            old_label.deleteLater()  # Правильное удаление Qt объекта
    
    def cleanup_old_messages(self, max_keep: int = 100):
        """
        ✅ FIX: Очищает старые сообщения для предотвращения утечки памяти.
        
        Args:
            max_keep: Максимальное количество labels для хранения
        """
        if len(self.labels) > max_keep:
            excess_count = len(self.labels) - max_keep
            for _ in range(excess_count):
                old_label = self.labels.pop(0)
                old_label.deleteLater()

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
                # Минимальная ширина теперь динамическая (300px вместо 500px)
                min_width = 300
                w = self.old_width + delta.x() if self.old_width + delta.x() > min_width else min_width
                h = self.old_height + delta.y() if self.old_height + delta.y() > 400 else 400
                self.setFixedSize(w, h)
            else:
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_Pos = event.globalPos()
