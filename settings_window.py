from PyQt5.Qt import *
import config


class SettingsWindow(QDialog):
    def __init__(self, config_obj, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.config = config_obj
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("⚙️ Настройки")
        self.setFixedSize(550, 750)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Применяем единый стиль как в TransGoogleTest
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(25, 30, 40, 230);
                border-radius: 12px;
                border: 2px solid rgba(40, 45, 55, 200);
            }
            QWidget {
                background-color: rgba(25, 30, 40, 230);
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                background-color: transparent;
            }
            QPushButton {
                background-color: rgba(40, 45, 55, 200);
                color: white;
                border: 1px solid rgba(60, 65, 75, 200);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(50, 55, 65, 200);
            }
            QPushButton:pressed {
                background-color: rgba(30, 35, 45, 200);
            }
            QLineEdit {
                background-color: rgba(40, 45, 55, 180);
                color: white;
                border: 1px solid rgba(60, 65, 75, 180);
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 32px;
            }
            QLineEdit:focus {
                border: 1px solid #6A1B9A;
            }
            QSlider::groove:horizontal {
                background: rgba(40, 45, 55, 180);
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6A1B9A;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: rgba(40, 45, 55, 180);
                color: white;
                border: 1px solid rgba(60, 65, 75, 180);
                border-radius: 4px;
                padding: 3px;
                font-size: 11px;
                min-width: 60px;
            }
            QGroupBox {
                color: #6A1B9A;
                font-weight: bold;
                background-color: rgba(35, 40, 50, 200);
                border: 1px solid rgba(60, 65, 75, 100);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            QScrollArea {
                border: none;
                background-color: rgba(25, 30, 40, 230);
            }
            QScrollArea > QWidget > QWidget {
                background-color: rgba(25, 30, 40, 230);
            }
        """)
        
        # Принудительно устанавливаем темный фон для основного виджета
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(25, 30, 40))
        self.setPalette(palette)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Скроллируемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: rgba(25, 30, 40, 230);")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        
        # Создаем поля для каждой настройки
        self.controls = {}
        
        # ==== ГРУППА: Внешний вид ====
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QGridLayout(appearance_group)
        appearance_layout.setVerticalSpacing(8)
        appearance_layout.setHorizontalSpacing(10)
        appearance_layout.setContentsMargins(12, 15, 12, 12)
        
        # Прозрачность окна
        appearance_layout.addWidget(QLabel("Прозрачность окна:"), 0, 0)
        
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(self.config.opacity * 100))
        
        self.opacity_value_label = QLabel(f"{int(self.config.opacity * 100)}%")
        self.opacity_value_label.setStyleSheet("color: #6A1B9A; font-weight: bold; min-width: 40px;")
        
        appearance_layout.addWidget(opacity_slider, 0, 1)
        appearance_layout.addWidget(self.opacity_value_label, 0, 2)
        
        opacity_slider.valueChanged.connect(lambda v: self.opacity_value_label.setText(f"{v}%"))
        self.controls['opacity'] = opacity_slider
        
        # Размер шрифта
        appearance_layout.addWidget(QLabel("Размер шрифта:"), 1, 0)
        
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 50)
        font_size_spin.setValue(self.config.font_size)
        font_size_spin.setFixedWidth(70)
        
        appearance_layout.addWidget(font_size_spin, 1, 1, 1, 2)
        self.controls['font_size'] = font_size_spin
        
        # Максимальное количество сообщений
        appearance_layout.addWidget(QLabel("Максимальное количество сообщений:"), 2, 0)
        
        max_messages_spin = QSpinBox()
        max_messages_spin.setRange(1, 100)
        max_messages_spin.setValue(self.config.max_messages)
        max_messages_spin.setFixedWidth(70)
        
        appearance_layout.addWidget(max_messages_spin, 2, 1, 1, 2)
        self.controls['max_messages'] = max_messages_spin
        
        scroll_layout.addWidget(appearance_group)
        
        # ==== ГРУППА: Распознавание речи ====
        recognition_group = QGroupBox("Распознавание речи")
        recognition_layout = QGridLayout(recognition_group)
        recognition_layout.setVerticalSpacing(8)
        recognition_layout.setHorizontalSpacing(10)
        recognition_layout.setContentsMargins(12, 15, 12, 12)
        
        # Частота дискретизации
        recognition_layout.addWidget(QLabel("Частота дискретизации (Гц):"), 0, 0)
        
        sample_rate_spin = QSpinBox()
        sample_rate_spin.setRange(8000, 48000)
        sample_rate_spin.setSingleStep(1000)
        sample_rate_spin.setValue(self.config.sample_rate)
        sample_rate_spin.setFixedWidth(100)
        
        recognition_layout.addWidget(sample_rate_spin, 0, 1, 1, 2)
        self.controls['sample_rate'] = sample_rate_spin
        
        # Порог энергии
        recognition_layout.addWidget(QLabel("Порог чувствительности микрофона:"), 1, 0)
        
        energy_slider = QSlider(Qt.Horizontal)
        energy_slider.setRange(100, 500)
        energy_slider.setValue(self.config.energy_threshold)
        
        self.energy_value_label = QLabel(f"{self.config.energy_threshold}")
        self.energy_value_label.setStyleSheet("color: #6A1B9A; font-weight: bold; min-width: 40px;")
        
        recognition_layout.addWidget(energy_slider, 1, 1)
        recognition_layout.addWidget(self.energy_value_label, 1, 2)
        
        energy_slider.valueChanged.connect(lambda v: self.energy_value_label.setText(f"{v}"))
        self.controls['energy_threshold'] = energy_slider
        
        # Порог паузы
        recognition_layout.addWidget(QLabel("Порог паузы:"), 2, 0)
        
        pause_spin = QDoubleSpinBox()
        pause_spin.setRange(0.1, 2.0)
        pause_spin.setSingleStep(0.1)
        pause_spin.setDecimals(2)
        pause_spin.setValue(self.config.pause_threshold)
        pause_spin.setFixedWidth(70)
        
        recognition_layout.addWidget(pause_spin, 2, 1, 1, 2)
        self.controls['pause_threshold'] = pause_spin
        
        # Индекс микрофона
        recognition_layout.addWidget(QLabel("Индекс выбранного микрофона:"), 3, 0)
        
        mic_index_spin = QSpinBox()
        mic_index_spin.setRange(0, 10)
        mic_index_spin.setValue(self.config.selected_mic_index)
        mic_index_spin.setFixedWidth(70)
        
        recognition_layout.addWidget(mic_index_spin, 3, 1, 1, 2)
        self.controls['selected_mic_index'] = mic_index_spin
        
        scroll_layout.addWidget(recognition_group)
        
        # ==== ГРУППА: Таймауты ====
        timeout_group = QGroupBox("Таймауты")
        timeout_layout = QGridLayout(timeout_group)
        timeout_layout.setVerticalSpacing(8)
        timeout_layout.setHorizontalSpacing(10)
        timeout_layout.setContentsMargins(12, 15, 12, 12)
        
        # Максимальная продолжительность записи
        timeout_layout.addWidget(QLabel("Максимальная продолжительность записи (сек):"), 0, 0)
        
        record_duration_spin = QSpinBox()
        record_duration_spin.setRange(10, 600)
        record_duration_spin.setSingleStep(10)
        record_duration_spin.setValue(self.config.record_duration)
        record_duration_spin.setFixedWidth(70)
        
        timeout_layout.addWidget(record_duration_spin, 0, 1, 1, 2)
        self.controls['record_duration'] = record_duration_spin
        
        # Таймаут ожидания речи
        timeout_layout.addWidget(QLabel("Таймаут ожидания речи (сек):"), 1, 0)
        
        listen_timeout_spin = QSpinBox()
        listen_timeout_spin.setRange(1, 60)
        listen_timeout_spin.setValue(self.config.listen_timeout)
        listen_timeout_spin.setFixedWidth(70)
        
        timeout_layout.addWidget(listen_timeout_spin, 1, 1, 1, 2)
        self.controls['listen_timeout'] = listen_timeout_spin
        
        # Максимальная длина фразы
        timeout_layout.addWidget(QLabel("Максимальная длина фразы (сек):"), 2, 0)
        
        phrase_time_limit_spin = QSpinBox()
        phrase_time_limit_spin.setRange(1, 60)
        phrase_time_limit_spin.setValue(self.config.phrase_time_limit)
        phrase_time_limit_spin.setFixedWidth(70)
        
        timeout_layout.addWidget(phrase_time_limit_spin, 2, 1, 1, 2)
        self.controls['phrase_time_limit'] = phrase_time_limit_spin
        
        scroll_layout.addWidget(timeout_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Кнопки (внизу, вне scroll area)
        button_widget = QWidget()
        button_widget.setStyleSheet("background-color: rgba(25, 30, 40, 230);")
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(15, 10, 15, 15)
        button_layout.setSpacing(12)
        
        ok_btn = QPushButton("✅ Применить")
        ok_btn.clicked.connect(self.save_settings)
        ok_btn.setFixedWidth(110)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(106, 27, 154, 200);
                border: 1px solid rgba(106, 27, 154, 220);
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(126, 47, 174, 200);
            }
        """)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFixedWidth(110)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 107, 107, 180);
                border: 1px solid rgba(255, 107, 107, 200);
            }
            QPushButton:hover {
                background-color: rgba(255, 127, 127, 180);
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        main_layout.addWidget(button_widget)
    
    def save_settings(self):
        """Сохраняет настройки в конфиг"""
        # Сохраняем значения из всех контролов
        for key, control in self.controls.items():
            if isinstance(control, QSlider) and key == 'opacity':
                # Для opacity слайдер дает значение 0-100, нужно разделить на 100
                value = control.value() / 100.0
            elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
                value = control.value()
            elif isinstance(control, QSlider):
                value = control.value()
            else:
                value = control.value()
            
            setattr(self.config, key, value)
        
        if self.config.save():
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки!")
