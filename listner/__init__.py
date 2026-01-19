import string
import time
from threading import Thread

import pyperclip as pc
import tkinter as tk
import speech_service as speach_service
import state
from listner import config_manager
import pyautogui
import keyboard

import speech_recognition as sr


class ListnerManger():
    def __init__(self, state, window):
        self.base_commands = ['система вернись', 'gorilla cup', 'говорилка', 'горилка', 'говорил', 'уважаемый']
        self.current_manager = "write"
        self.commands = ['поговори со мной', 'theresa may', 'play some movie']
        self.commands_state = ['case', 'keys', 'gypsy rose', 'айз', 'smokies', 'is up', 'is ap', 'activate',
                               'gpt подскажи']
        self.state = state
        self.window = window
        self.his = []
        self.his_arr = []
        self.managers = [
            speach_service.SpeechService(),
            config_manager.ConfigManger(self)
        ]
        self.r = sr.Recognizer()
        self.managers_process = [
            self
        ]

    def process(self, speach_resul):
        str = self.get_string(speach_resul=speach_resul)
        if not str:
            return False
        print("Listner:" + self.state.listner)
        self.process_write(str)

    def process_write(self, str: str):
        str = self.state.getStr(str)
        self.save(str)
        self.write(str)

    def is_command_write(self, str):
        for i in self.base_commands:
            print(i)
            print(str.find(i) and str.find(i) != -1)
            if str.find(i) != -1:
                speach_service.speech('Базовый режим', speach_service.LANG_RUS)
                return True
        return False

    def concat_str(self, str):
        if not self.his:
            return str
        str_arr = str.split(" ")
        i = None
        for s in list(reversed(str_arr)):
            rindex = "".join(list(reversed(self.his[0]))).find(''.join(list(reversed(s))))
            if rindex != -1:
                i = len(self.his[0]) - rindex - len(s)
                break
        if i and str.find(self.his[0][i:]) != -1:
            str = self.his[0][:i] + str
        return str

    def get_string(self, speach_resul):
        return speach_resul['alternative'][0]['transcript'].lower() if speach_resul and speach_resul['alternative'][0] else  None

    def to_console(self, string):
        print(string)

    def save(self, str):
        # Проверяем что текст не пустой
        if not str or not str.strip():
            return
            
        config = self.state.Config if hasattr(self.state, 'Config') else None
        
        if not config:
            return
        
        # Копируем в буфер обмена, если включено
        if config.output_clipboard:
            try:
                pc.copy(str)
            except Exception as e:
                print(f"Ошибка копирования в буфер обмена: {e}")
        
        # Вставляем в текстовый курсор, если включено
        if config.output_text_cursor:
            try:
                # Всегда копируем текст в буфер обмена перед вставкой (даже если output_clipboard включен)
                # Это гарантирует, что текст точно будет в буфере при вставке
                pc.copy(str)
                # Задержка для надежного копирования
                time.sleep(0.15)
                
                # Проверяем что текст действительно в буфере
                try:
                    clipboard_check = pc.paste()
                    if clipboard_check != str:
                        # Если текст не совпадает, копируем еще раз
                        pc.copy(str)
                        time.sleep(0.15)
                except:
                    pass
                
                # Вставляем через Ctrl+V
                # Используем keyboard вместо pyautogui для более надежной работы
                try:
                    # Используем keyboard для надежной отправки
                    keyboard.send('ctrl+v')
                    time.sleep(0.1)
                except:
                    # Fallback на pyautogui
                    try:
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.1)
                    except Exception as e2:
                        print(f'pyautogui.hotkey also failed: {e2}')
            except Exception as e:
                print(f"Ошибка вставки текста в курсор: {e}")
                import traceback
                traceback.print_exc()
        
        # Для обратной совместимости с fastWrite
        if self.state.fastWrite:
            try:
                pyautogui.typewrite(str)
            except Exception as e:
                print(f'pyautogui.typewrite failed: {e}')

        rhis = list(reversed(self.his))
        rhis.append(str)
        if len(rhis) > 3:
            rhis.pop(0)
        self.his = list(reversed(rhis))

    def write(self, str):
        # self.window.labels[0].setText(string)
        # Показываем в интерфейсе только если включено в настройках
        config = self.state.Config if hasattr(self.state, 'Config') else None
        
        if config and config.output_interface:
            self.window.addAnswer(str)
        else:
            # Если интерфейс выключен, все равно запускаем автоскрытие для окна (если оно видимо)
            # Это нужно для корректной работы автоскрытия
            if self.window.isVisible() and hasattr(self.window, 'schedule_auto_hide'):
                self.window.schedule_auto_hide()

    def last_rebuld(self):
        for str in self.his:
            str = self.state.getStr(str)
            self.save(str)
            self.write(str)

    def is_commands(self, str):
        for c in self.commands:
            if str.find(c) != -1:
                return str
        return False

    def is_commands_state(self, str):
        for c in self.commands_state:
            if str.find(c) != -1:
                return str
        return False

    def get_command_secification(self, str):
        for m in self.managers:
            print(self, m, str, m.is_spec(str))
            if m.is_spec(str):
                m.run(str)
                return m

    def is_process(self):
        if self.state != self.current_manager:
            return True
        return False

    def get_process_secification(self):
        for m in self.managers_process:
            if m.is_spec_proc(self.state.current_manager):
                return m.run()

    def pocessAudio(self, data):
        result = self.r.recognize_google(data, language=self.state.get_keyboard_language(), show_all=True)

        str = self.get_string(speach_resul=result)
        if not str:
            return

        c = self.is_commands(str)
        if c:
            self.state.listner = 'manager'

        c = self.is_commands_state(str)
        if c:
            self.get_command_secification(str)

        pr = Thread(target=self.process, args=(result,))
        pr.start()