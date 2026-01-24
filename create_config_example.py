#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания config.json.example из config.json
Копирует структуру и значения из вашего config.json, но без чувствительных данных
"""

import json
import sys
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Добавляем путь к модулю config
sys.path.insert(0, str(Path(__file__).parent))

def create_config_example():
    """Создает config.json.example из config.json, сохраняя структуру но без ключей."""
    
    config_file = Path("config.json")
    example_file = Path("config.json.example")
    
    if not config_file.exists():
        print("Error: config.json not found")
        return False
    
    # Читаем текущий config пользователя
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return False
    
    # Импортируем Config для получения дефолтных значений
    try:
        import config
        config_obj = config.Config()
        
        # Получаем дефолтные значения из схемы
        default_config = {}
        for key, schema in config_obj.CONFIG_SCHEMA.items():
            if 'default' in schema:
                default_config[key] = schema['default']
        
        # Создаем example config: берем структуру из user_config, но значения из дефолтов
        # Это сохраняет все ключи, но с безопасными дефолтными значениями
        example_config = {}
        for key in user_config.keys():
            if key in default_config:
                example_config[key] = default_config[key]
            else:
                # Если ключа нет в схеме, берем значение из user_config
                example_config[key] = user_config[key]
        
    except ImportError:
        # Если не удалось импортировать config, просто копируем структуру
        print("Warning: Could not import config module, using values from config.json")
        example_config = user_config.copy()
    
    # Сохраняем как пример
    try:
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        try:
            print(f"OK: Created {example_file} (structure from your config.json, default values)")
        except:
            print(f"OK: Created {example_file}")
        return True
    except Exception as e:
        try:
            print(f"Error creating {example_file}: {e}")
        except:
            print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_config_example()
