from PyQt5.Qt import *
import config
from audio_recorder import get_available_microphones, get_default_microphone_index


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
            QCheckBox {
                color: white;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #6A1B9A;
                border-radius: 4px;
                background-color: rgba(40, 45, 55, 180);
            }
            QCheckBox::indicator:checked {
                background-color: #6A1B9A;
            }
            QComboBox {
                background-color: rgba(40, 45, 55, 180);
                color: white;
                border: 1px solid rgba(60, 65, 75, 180);
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
                min-height: 28px;
            }
            QComboBox:hover {
                border: 1px solid #6A1B9A;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(40, 45, 55, 250);
                color: white;
                selection-background-color: #6A1B9A;
                selection-color: white;
                border: 1px solid rgba(60, 65, 75, 180);
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
        
        # Длительность отображения (0 = не пропадать)
        appearance_layout.addWidget(QLabel("Длительность отображения (сек, 0=не пропадать):"), 3, 0)
        
        auto_hide_duration_spin = QSpinBox()
        auto_hide_duration_spin.setRange(0, 300)
        auto_hide_duration_spin.setValue(self.config.auto_hide_duration)
        auto_hide_duration_spin.setFixedWidth(70)
        auto_hide_duration_spin.setToolTip("0 = окно не будет автоматически скрываться")
        
        appearance_layout.addWidget(auto_hide_duration_spin, 3, 1, 1, 2)
        self.controls['auto_hide_duration'] = auto_hide_duration_spin
        
        # Язык интерфейса
        appearance_layout.addWidget(QLabel("Язык интерфейса:"), 4, 0)
        
        language_combo = QComboBox()
        language_combo.addItem("Русский (ru)", "ru")
        language_combo.addItem("English (en)", "en")
        language_combo.addItem("Українська (uk)", "uk")
        language_combo.addItem("Deutsch (de)", "de")
        language_combo.addItem("Français (fr)", "fr")
        language_combo.addItem("Español (es)", "es")
        
        # Устанавливаем текущий язык
        current_lang = getattr(self.config, 'language', 'ru')
        for i in range(language_combo.count()):
            if language_combo.itemData(i) == current_lang:
                language_combo.setCurrentIndex(i)
                break
        
        appearance_layout.addWidget(language_combo, 4, 1, 1, 2)
        self.controls['language'] = language_combo
        
        scroll_layout.addWidget(appearance_group)
        
        # ==== ГРУППА: Вывод сообщений ====
        output_group = QGroupBox("Вывод сообщений")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(8)
        output_layout.setContentsMargins(12, 15, 12, 12)
        
        # Чекбоксы для выбора куда вводить сообщение
        output_interface_checkbox = QCheckBox("Интерфейс (показывать в окне)")
        output_interface_checkbox.setChecked(self.config.output_interface)
        output_layout.addWidget(output_interface_checkbox)
        self.controls['output_interface'] = output_interface_checkbox
        
        output_clipboard_checkbox = QCheckBox("Буфер обмена (копировать)")
        output_clipboard_checkbox.setChecked(self.config.output_clipboard)
        output_layout.addWidget(output_clipboard_checkbox)
        self.controls['output_clipboard'] = output_clipboard_checkbox
        
        output_text_cursor_checkbox = QCheckBox("Текстовый курсор (вводить в активное поле)")
        output_text_cursor_checkbox.setChecked(self.config.output_text_cursor)
        output_layout.addWidget(output_text_cursor_checkbox)
        self.controls['output_text_cursor'] = output_text_cursor_checkbox
        
        scroll_layout.addWidget(output_group)
        
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
        
        # Выбор микрофона
        recognition_layout.addWidget(QLabel("🎤 Микрофон:"), 3, 0)
        
        mic_combo = QComboBox()
        mic_combo.setToolTip("Выберите микрофон для распознавания речи")
        
        # Получаем список доступных микрофонов
        try:
            available_mics = get_available_microphones()
            default_index = get_default_microphone_index()
            
            if available_mics:
                for mic in available_mics:
                    # Формат: "🎤 Название (ID: X, каналов: Y)"
                    display_text = f"{mic['name']} (ID: {mic['index']}, {mic['channels']}ch, {mic['sample_rate']}Hz)"
                    mic_combo.addItem(display_text, mic['index'])  # userData = device index
                
                # Устанавливаем текущий выбранный микрофон
                for i in range(mic_combo.count()):
                    if mic_combo.itemData(i) == self.config.selected_mic_index:
                        mic_combo.setCurrentIndex(i)
                        break
                else:
                    # Если сохраненный индекс не найден, выбираем default
                    for i in range(mic_combo.count()):
                        if mic_combo.itemData(i) == default_index:
                            mic_combo.setCurrentIndex(i)
                            break
            else:
                mic_combo.addItem("⚠️ Микрофоны не найдены", 0)
                mic_combo.setEnabled(False)
        except Exception as e:
            mic_combo.addItem(f"❌ Ошибка: {str(e)}", 0)
            mic_combo.setEnabled(False)
        
        recognition_layout.addWidget(mic_combo, 3, 1, 1, 2)
        self.controls['selected_mic_index'] = mic_combo
        
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
        
        # ==== ГРУППА: Горячая клавиша ====
        hotkey_group = QGroupBox("⌨️ Горячая клавиша")
        hotkey_layout = QVBoxLayout(hotkey_group)
        hotkey_layout.setSpacing(8)
        hotkey_layout.setContentsMargins(12, 15, 12, 12)
        
        # Описание
        hotkey_description = QLabel(
            "Комбинация клавиш для активации распознавания речи.\n"
            "Используйте модификаторы: ctrl, alt, shift, win + клавиша.\n"
            "Примеры: ctrl+shift+f5, ctrl+alt+space, win+shift+r"
        )
        hotkey_description.setWordWrap(True)
        hotkey_description.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 10px; padding: 5px;")
        hotkey_layout.addWidget(hotkey_description)
        
        # Поле для ввода горячей клавиши
        hotkey_container = QWidget()
        hotkey_container_layout = QHBoxLayout(hotkey_container)
        hotkey_container_layout.setContentsMargins(0, 0, 0, 0)
        hotkey_container_layout.setSpacing(10)
        
        hotkey_label = QLabel("Комбинация:")
        hotkey_container_layout.addWidget(hotkey_label)
        
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(self.config.hotkey)
        self.hotkey_input.setPlaceholderText("ctrl+shift+win+f5")
        self.hotkey_input.setToolTip("Введите комбинацию клавиш, например: ctrl+shift+f5")
        hotkey_container_layout.addWidget(self.hotkey_input)
        
        # Кнопка "Записать" для захвата нажатия клавиш
        self.record_hotkey_btn = QPushButton("🎤 Записать")
        self.record_hotkey_btn.setToolTip("Нажмите и затем нажмите желаемую комбинацию клавиш")
        self.record_hotkey_btn.setFixedWidth(120)
        self.record_hotkey_btn.clicked.connect(self.start_recording_hotkey)
        hotkey_container_layout.addWidget(self.record_hotkey_btn)
        
        hotkey_layout.addWidget(hotkey_container)
        
        # Статус записи
        self.hotkey_status = QLabel("")
        self.hotkey_status.setStyleSheet("color: #6A1B9A; font-size: 11px; padding: 5px;")
        self.hotkey_status.setVisible(False)
        hotkey_layout.addWidget(self.hotkey_status)
        
        # Популярные комбинации
        popular_hotkeys_label = QLabel("Популярные комбинации:")
        popular_hotkeys_label.setStyleSheet("color: rgba(255, 255, 255, 200); font-size: 11px; margin-top: 5px;")
        hotkey_layout.addWidget(popular_hotkeys_label)
        
        popular_container = QWidget()
        popular_layout = QHBoxLayout(popular_container)
        popular_layout.setContentsMargins(0, 0, 0, 0)
        popular_layout.setSpacing(5)
        
        popular_hotkeys = [
            "ctrl+shift+win+f5",
            "ctrl+alt+space",
            "ctrl+shift+r",
            "win+shift+s"
        ]
        
        for hotkey in popular_hotkeys:
            btn = QPushButton(hotkey)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(106, 27, 154, 100);
                    border: 1px solid #6A1B9A;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(106, 27, 154, 150);
                }
            """)
            btn.clicked.connect(lambda checked, h=hotkey: self.hotkey_input.setText(h))
            popular_layout.addWidget(btn)
        
        popular_layout.addStretch()
        hotkey_layout.addWidget(popular_container)
        
        self.controls['hotkey'] = self.hotkey_input
        
        scroll_layout.addWidget(hotkey_group)
        
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
    
    def start_recording_hotkey(self):
        """Начинает запись горячей клавиши."""
        self.record_hotkey_btn.setText("⏺ Нажмите клавиши...")
        self.record_hotkey_btn.setEnabled(False)
        self.hotkey_status.setText("Ожидание нажатия клавиш...")
        self.hotkey_status.setVisible(True)
        
        # Устанавливаем фокус на окно для захвата клавиш
        self.setFocus()
        self.is_recording_hotkey = True
        self.recorded_keys = []
    
    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш для записи горячей клавиши."""
        if not hasattr(self, 'is_recording_hotkey') or not self.is_recording_hotkey:
            super().keyPressEvent(event)
            return
        
        # Словарь для преобразования Qt клавиш в формат keyboard
        key_map = {
            Qt.Key_Control: 'ctrl',
            Qt.Key_Alt: 'alt',
            Qt.Key_Shift: 'shift',
            Qt.Key_Meta: 'win',
            Qt.Key_F1: 'f1', Qt.Key_F2: 'f2', Qt.Key_F3: 'f3', Qt.Key_F4: 'f4',
            Qt.Key_F5: 'f5', Qt.Key_F6: 'f6', Qt.Key_F7: 'f7', Qt.Key_F8: 'f8',
            Qt.Key_F9: 'f9', Qt.Key_F10: 'f10', Qt.Key_F11: 'f11', Qt.Key_F12: 'f12',
            Qt.Key_Space: 'space',
            Qt.Key_Return: 'enter',
            Qt.Key_Enter: 'enter',
            Qt.Key_Tab: 'tab',
            Qt.Key_Backspace: 'backspace',
            Qt.Key_Delete: 'delete',
            Qt.Key_Insert: 'insert',
            Qt.Key_Home: 'home',
            Qt.Key_End: 'end',
            Qt.Key_PageUp: 'page up',
            Qt.Key_PageDown: 'page down',
        }
        
        modifiers = []
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append('ctrl')
        if event.modifiers() & Qt.AltModifier:
            modifiers.append('alt')
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append('shift')
        if event.modifiers() & Qt.MetaModifier:
            modifiers.append('win')
        
        # Получаем основную клавишу
        key = event.key()
        key_str = key_map.get(key, event.text().lower())
        
        # Игнорируем если только модификаторы
        if key in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta]:
            return
        
        # Формируем hotkey строку
        if modifiers and key_str:
            hotkey = '+'.join(modifiers + [key_str])
            self.hotkey_input.setText(hotkey)
            self.hotkey_status.setText(f"✅ Записано: {hotkey}")
            self.hotkey_status.setStyleSheet("color: #4CAF50; font-size: 11px; padding: 5px;")
        else:
            self.hotkey_status.setText("❌ Нужна комбинация с модификатором")
            self.hotkey_status.setStyleSheet("color: #F44336; font-size: 11px; padding: 5px;")
        
        # Сбрасываем режим записи
        self.is_recording_hotkey = False
        self.record_hotkey_btn.setText("🎤 Записать")
        self.record_hotkey_btn.setEnabled(True)
    
    def save_settings(self):
        """Сохраняет настройки в конфиг"""
        # Сохраняем значения из всех контролов
        for key, control in self.controls.items():
            if isinstance(control, QSlider) and key == 'opacity':
                # Для opacity слайдер дает значение 0-100, нужно разделить на 100
                value = control.value() / 100.0
            elif isinstance(control, QComboBox):
                # Для микрофона и языка - берем userData
                value = control.currentData()
                if value is None:
                    # Если это микрофон, то 0, если язык - то 'ru'
                    if key == 'selected_mic_index':
                        value = 0
                    elif key == 'language':
                        value = 'ru'
                    else:
                        value = 0
            elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
                value = control.value()
            elif isinstance(control, QSlider):
                value = control.value()
            elif isinstance(control, QCheckBox):
                value = control.isChecked()
            elif isinstance(control, QLineEdit):
                # ✅ Поддержка QLineEdit для hotkey
                value = control.text()
            elif isinstance(control, QComboBox) and key == 'language':
                # ✅ Для языка берем userData
                value = control.currentData()
                if value is None:
                    value = 'ru'  # По умолчанию русский
            else:
                value = control.value()
            
            setattr(self.config, key, value)
        
        if self.config.save():
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки!")
