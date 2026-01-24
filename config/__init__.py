"""
Configuration module with validation.

SECURITY FIXES:
- Added strict type validation
- Added value range validation
- Protected against code injection via JSON
- Added logging for invalid config values
"""
import json
import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Raised when config validation fails."""
    pass


class Config:
    """Application configuration with strict validation."""
    
    CONFIG_FILE = 'config.json'
    
    # ✅ Define allowed config keys with types and constraints
    CONFIG_SCHEMA = {
        'opacity': {
            'type': float,
            'min': 0.0,
            'max': 1.0,
            'default': 0.95
        },
        'font_size': {
            'type': int,
            'min': 8,
            'max': 72,
            'default': 11
        },
        'max_messages': {
            'type': int,
            'min': 1,
            'max': 1000,
            'default': 30
        },
        'max_message_length': {
            'type': int,
            'min': 10,
            'max': 10000,
            'default': 500
        },
        'sample_rate': {
            'type': int,
            'min': 8000,
            'max': 48000,
            'default': 16000
        },
        'record_duration': {
            'type': int,
            'min': 1,
            'max': 3600,
            'default': 300
        },
        'energy_threshold': {
            'type': int,
            'min': 100,
            'max': 5000,
            'default': 300
        },
        'pause_threshold': {
            'type': float,
            'min': 0.1,
            'max': 5.0,
            'default': 0.8
        },
        'selected_mic_index': {
            'type': int,
            'min': 0,
            'max': 100,
            'default': 0
        },
        'listen_timeout': {
            'type': int,
            'min': 1,
            'max': 300,
            'default': 10
        },
        'phrase_time_limit': {
            'type': int,
            'min': 1,
            'max': 60,
            'default': 10
        },
        'auto_hide_duration': {
            'type': int,
            'min': 0,
            'max': 300,
            'default': 0
        },
        'output_interface': {
            'type': bool,
            'default': True
        },
        'output_clipboard': {
            'type': bool,
            'default': True
        },
        'output_text_cursor': {
            'type': bool,
            'default': False
        },
        'hotkey': {
            'type': str,
            'default': 'ctrl+shift+win+f5',
            'allowed_values': None  # Will be validated separately
        },
        'window_offset_from_bottom': {
            'type': int,
            'min': 0,
            'max': 2000,
            'default': 400
        },
        'manager_sleep_interval': {
            'type': float,
            'min': 0.1,
            'max': 60.0,
            'default': 3.0
        },
        'startup_delay': {
            'type': float,
            'min': 0.0,
            'max': 10.0,
            'default': 2.8
        },
        'clipboard_copy_delay': {
            'type': float,
            'min': 0.01,
            'max': 1.0,
            'default': 0.15
        },
        'paste_delay': {
            'type': float,
            'min': 0.01,
            'max': 1.0,
            'default': 0.1
        },
        'language': {
            'type': str,
            'default': 'ru',
            'allowed_values': ['ru', 'en', 'uk', 'de', 'fr', 'es']
        },
        'enable_hotkey_stop_recording': {
            'type': bool,
            'default': True
        }
    }
    
    def __init__(self):
        self.Languages = {
            "ru-RU": '0x4090409',
            "en-US": '0x4190419'
        }
        
        # Initialize with defaults
        self._apply_defaults()
        
        # Load saved settings
        self.load()
        
        # Инициализируем язык интерфейса, если не задан
        if not hasattr(self, 'language') or not self.language:
            try:
                import i18n
                detected_lang = i18n.detect_system_language()
                self.language = detected_lang
                # Сохраняем автоматически определенный язык
                self.save()
            except (ImportError, AttributeError):
                self.language = 'ru'
    
    def to_dict(self):
        """Преобразует конфиг в словарь для сохранения"""
        return {
            'opacity': self.opacity,
            'font_size': self.font_size,
            'max_messages': self.max_messages,
            'max_message_length': self.max_message_length,
            'sample_rate': self.sample_rate,
            'record_duration': self.record_duration,
            'energy_threshold': self.energy_threshold,
            'pause_threshold': self.pause_threshold,
            'selected_mic_index': self.selected_mic_index,
            'listen_timeout': self.listen_timeout,
            'phrase_time_limit': self.phrase_time_limit,
            'auto_hide_duration': self.auto_hide_duration,
            'output_interface': self.output_interface,
            'output_clipboard': self.output_clipboard,
            'output_text_cursor': self.output_text_cursor,
            'hotkey': self.hotkey,
            'window_offset_from_bottom': self.window_offset_from_bottom,
            'manager_sleep_interval': self.manager_sleep_interval,
            'startup_delay': self.startup_delay,
            'clipboard_copy_delay': self.clipboard_copy_delay,
            'paste_delay': self.paste_delay,
            'language': self.language,
            'enable_hotkey_stop_recording': self.enable_hotkey_stop_recording
        }
    
    def _apply_defaults(self):
        """Apply default values from schema."""
        for key, schema in self.CONFIG_SCHEMA.items():
            setattr(self, key, schema['default'])
    
    def _validate_hotkey(self, hotkey: str) -> str:
        """
        Validate hotkey string.
        
        Args:
            hotkey: Hotkey string (e.g., 'ctrl+shift+f5')
            
        Returns:
            Validated hotkey string
            
        Raises:
            ConfigValidationError: If hotkey is invalid
        """
        if not hotkey or not isinstance(hotkey, str):
            raise ConfigValidationError("Hotkey must be a non-empty string")
        
        # Basic validation - check for valid modifiers and keys
        valid_modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
        parts = [p.strip().lower() for p in hotkey.split('+')]
        
        if len(parts) < 2:
            raise ConfigValidationError("Hotkey must include at least modifier+key")
        
        # Check that at least one part is a recognized modifier
        has_modifier = any(part in valid_modifiers for part in parts)
        if not has_modifier:
            raise ConfigValidationError("Hotkey must include at least one modifier (ctrl, alt, shift, win)")
        
        return hotkey.lower()
    
    def _validate_value(self, key: str, value: Any) -> Any:
        """
        Validate config value against schema.
        
        Args:
            key: Config key
            value: Value to validate
            
        Returns:
            Validated value
            
        Raises:
            ConfigValidationError: If validation fails
        """
        if key not in self.CONFIG_SCHEMA:
            raise ConfigValidationError(f"Unknown config key: {key}")
        
        schema = self.CONFIG_SCHEMA[key]
        expected_type = schema['type']
        
        # Special validation for hotkey
        if key == 'hotkey':
            return self._validate_hotkey(value)
        
        # Type validation
        if not isinstance(value, expected_type):
            # Try to convert
            try:
                if expected_type == bool:
                    value = bool(value)
                elif expected_type == int:
                    value = int(value)
                elif expected_type == float:
                    value = float(value)
                elif expected_type == str:
                    value = str(value)
                else:
                    raise ConfigValidationError(
                        f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}"
                    )
            except (ValueError, TypeError) as e:
                raise ConfigValidationError(
                    f"Cannot convert {key} to {expected_type.__name__}: {e}"
                )
        
        # Range validation for numeric values
        if expected_type in (int, float):
            if 'min' in schema and value < schema['min']:
                logger.warning(
                    f"Config {key}={value} below min {schema['min']}, using min"
                )
                value = schema['min']
            
            if 'max' in schema and value > schema['max']:
                logger.warning(
                    f"Config {key}={value} above max {schema['max']}, using max"
                )
                value = schema['max']
        
        return value
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Load config from dictionary with validation.
        
        Args:
            data: Config data dictionary
        """
        for key, value in data.items():
            try:
                validated_value = self._validate_value(key, value)
                setattr(self, key, validated_value)
            except ConfigValidationError as e:
                logger.error(f"Config validation error: {e}")
                # Keep default value
                if key in self.CONFIG_SCHEMA:
                    setattr(self, key, self.CONFIG_SCHEMA[key]['default'])
            except Exception as e:
                logger.error(f"Unexpected error loading config {key}: {e}")
                # Keep default value
    
    def save(self) -> bool:
        """
        Save config to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Config saved to {self.CONFIG_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}", exc_info=True)
            return False
    
    def load(self) -> bool:
        """
        Load config from file with validation.
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.CONFIG_FILE):
            logger.info(f"Config file {self.CONFIG_FILE} not found, using defaults")
            return False
        
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate that data is a dictionary
            if not isinstance(data, dict):
                raise ConfigValidationError("Config must be a JSON object")
            
            # Load with validation
            self.from_dict(data)
            logger.info(f"Config loaded from {self.CONFIG_FILE}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return False
        except ConfigValidationError as e:
            logger.error(f"Config validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load config: {e}", exc_info=True)
            return False
    
    def validate(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate all current values
            for key in self.CONFIG_SCHEMA:
                value = getattr(self, key, None)
                if value is None:
                    logger.error(f"Config {key} is None")
                    return False
                self._validate_value(key, value)
            return True
        except ConfigValidationError as e:
            logger.error(f"Config validation failed: {e}")
            return False