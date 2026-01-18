import array
import locale
import json
import os


class Config():
    CONFIG_FILE = 'config.json'
    
    def __init__(self):
        self.Languages = dict()
        self.Languages["ru-RU"] = '0x4090409'
        self.Languages["en-US"] = '0x4190419'
        
        # Значения по умолчанию из promt.txt
        self.opacity = 0.95
        self.font_size = 11
        self.max_messages = 30
        self.sample_rate = 16000
        self.record_duration = 300
        self.energy_threshold = 300
        self.pause_threshold = 0.8
        self.selected_mic_index = 0
        self.listen_timeout = 10
        self.phrase_time_limit = 10
        
        # Загружаем сохраненные настройки
        self.load()
    
    def to_dict(self):
        """Преобразует конфиг в словарь для сохранения"""
        return {
            'opacity': self.opacity,
            'font_size': self.font_size,
            'max_messages': self.max_messages,
            'sample_rate': self.sample_rate,
            'record_duration': self.record_duration,
            'energy_threshold': self.energy_threshold,
            'pause_threshold': self.pause_threshold,
            'selected_mic_index': self.selected_mic_index,
            'listen_timeout': self.listen_timeout,
            'phrase_time_limit': self.phrase_time_limit
        }
    
    def from_dict(self, data):
        """Загружает конфиг из словаря"""
        self.opacity = data.get('opacity', 0.95)
        self.font_size = data.get('font_size', 11)
        self.max_messages = data.get('max_messages', 30)
        self.sample_rate = data.get('sample_rate', 16000)
        self.record_duration = data.get('record_duration', 300)
        self.energy_threshold = data.get('energy_threshold', 300)
        self.pause_threshold = data.get('pause_threshold', 0.8)
        self.selected_mic_index = data.get('selected_mic_index', 0)
        self.listen_timeout = data.get('listen_timeout', 10)
        self.phrase_time_limit = data.get('phrase_time_limit', 10)
    
    def save(self):
        """Сохраняет конфиг в файл"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
            return False
    
    def load(self):
        """Загружает конфиг из файла"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.from_dict(data)
                return True
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")
                return False
        return False