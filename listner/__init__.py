"""
Модуль для обработки распознанной речи.

Содержит ListnerManger класс, который обрабатывает результаты распознавания
и выводит текст в различные места (UI, буфер обмена, текстовый курсор).
"""
import time
from typing import Dict, Any, Optional

import pyperclip as pc
import state
import pyautogui
import keyboard

import speech_recognition as sr

from logger_config import get_logger

logger = get_logger(__name__)


class ListnerManger:
    """
    Менеджер распознавания речи.
    Обрабатывает результаты распознавания и выводит текст в разные места
    (UI, буфер обмена, текстовый курсор).
    """
    
    def __init__(self, state: 'state.State', window: Any) -> None:
        """
        Инициализирует менеджер.
        
        Args:
            state: Состояние приложения
            window: Главное окно приложения (MainWindow)
        """
        self.state: 'state.State' = state
        self.window: Any = window
        self.his: List[str] = []  # История последних сообщений
        self.r: sr.Recognizer = sr.Recognizer()

    def process(self, speech_result: Dict[str, Any]) -> bool:
        """
        Обрабатывает результат распознавания речи.
        
        Args:
            speech_result: Результат от Google Speech API
            
        Returns:
            True если текст был обработан, False если текст пустой
        """
        text = self.get_string(speech_result=speech_result)
        if not text:
            return False
        self.process_write(text)
        return True

    def process_write(self, text: str) -> None:
        """
        Обрабатывает и выводит распознанный текст.
        
        Args:
            text: Распознанный текст
        """
        text = self.state.getStr(text)
        self.save(text)
        self.write(text)

    def get_string(self, speech_result: Dict[str, Any]) -> Optional[str]:
        """
        Извлекает текст из результата распознавания Google Speech API.
        
        Args:
            speech_result: Результат от Google Speech API
            
        Returns:
            Распознанный текст или None если распознавание не удалось
        """
        try:
            if speech_result and speech_result.get('alternative') and speech_result['alternative'][0]:
                return speech_result['alternative'][0]['transcript'].lower()
        except (KeyError, IndexError, TypeError):
            pass
        return None

    def save(self, text: str) -> None:
        """
        Сохраняет текст в буфер обмена и/или вставляет в текстовый курсор.
        
        Args:
            text: Текст для сохранения
        """
        # Проверяем что текст не пустой
        if not text or not text.strip():
            return
            
        config = self.state.Config if hasattr(self.state, 'Config') else None
        
        if not config:
            return
        
        # Копируем в буфер обмена, если включено
        if config.output_clipboard:
            try:
                pc.copy(text)
            except Exception as e:
                logger.error(f"Ошибка копирования в буфер обмена: {e}", exc_info=True)
        
        # Вставляем в текстовый курсор, если включено
        if config.output_text_cursor:
            try:
                # Всегда копируем текст в буфер обмена перед вставкой (даже если output_clipboard включен)
                # Это гарантирует, что текст точно будет в буфере при вставке
                pc.copy(text)
                # Задержка для надежного копирования
                config = self.state.Config if hasattr(self.state, 'Config') else None
                delay = config.clipboard_copy_delay if config else 0.15
                time.sleep(delay)
                
                # Проверяем что текст действительно в буфере
                try:
                    clipboard_check = pc.paste()
                    if clipboard_check != text:
                        # Если текст не совпадает, копируем еще раз
                        pc.copy(text)
                        time.sleep(delay)
                except:
                    pass
                
                # Вставляем через Ctrl+V
                # Используем keyboard вместо pyautogui для более надежной работы
                try:
                    # Используем keyboard для надежной отправки
                    keyboard.send('ctrl+v')
                    paste_delay = config.paste_delay if config else 0.1
                    time.sleep(paste_delay)
                except:
                    # Fallback на pyautogui
                    try:
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(paste_delay)
                    except Exception as e2:
                        print(f'pyautogui.hotkey also failed: {e2}')
            except Exception as e:
                print(f"Ошибка вставки текста в курсор: {e}")
                import traceback
                traceback.print_exc()
        
        # Для обратной совместимости с fastWrite
        if self.state.fastWrite:
            try:
                pyautogui.typewrite(text)
            except Exception as e:
                print(f'pyautogui.typewrite failed: {e}')

        rhis = list(reversed(self.his))
        rhis.append(text)
        if len(rhis) > 3:
            rhis.pop(0)
        self.his = list(reversed(rhis))

    def write(self, text: str) -> None:
        """
        Отображает текст в UI окне.
        
        Args:
            text: Текст для отображения
        """
        # self.window.labels[0].setText(string)
        # Показываем в интерфейсе только если включено в настройках
        config = self.state.Config if hasattr(self.state, 'Config') else None
        
        if config and config.output_interface:
            self.window.addAnswer(text)
        else:
            # Если интерфейс выключен, все равно запускаем автоскрытие для окна (если оно видимо)
            # Это нужно для корректной работы автоскрытия
            if self.window.isVisible() and hasattr(self.window, 'schedule_auto_hide'):
                self.window.schedule_auto_hide()
