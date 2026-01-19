"""
State module for managing application state.

Contains State class for managing keyboard language and other application state.
"""
import ctypes
from typing import Dict

import config as config_module

EN_US = "en-US"


class State:
    """Manages application state including keyboard language."""
    
    def __init__(self, config: 'config_module.Config') -> None:
        """
        Initialize state.
        
        Args:
            config: Application configuration
        """
        self.Config: 'config_module.Config' = config
        self.listner: str = "write"
        self.active: bool = False

        self.fastWrite: bool = False
        self.is_up: bool = False

        self.languages: Dict[str, str] = {
            '0x419': "ru-RU",
            '0x409': "en-US",
        }
        self.languages_for_speacher_service: Dict[str, str] = {
            '0x419': "ru",
            '0x409': "en-US",
        }

    def getStr(self, text: str) -> str:
        """
        Returns text as-is (no transformations).
        
        Args:
            text: Input text
            
        Returns:
            The same text unchanged
        """
        return text

    def get_keyboard_language(self) -> str:
        """
        Get current keyboard language layout.
        
        Returns:
            Language code ("ru-RU" or "en-US")
        """
        languages = {
            '0x419': "ru-RU",
            '0x409': EN_US,
        }
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        handle = user32.GetForegroundWindow()
        threadid = user32.GetWindowThreadProcessId(handle, 0)
        layout_id = user32.GetKeyboardLayout(threadid)
        language_id = layout_id & (2 ** 16 - 1)
        language_id_hex = hex(language_id)
        if language_id_hex in languages.keys():
            return languages[language_id_hex]
        else:
            return languages['0x419']
