import ctypes
import re

EN_US = "en-US"

CASE_DEFAULT = 0
CASE_CAMEL = 1
CASE_SNAKE = 2

class State():
    def __init__(self, config):
        self.case = 0
        self.Config = config
        self.listner = "write"
        self.active = False

        self.fastWrite = False
        self.is_up = False

        self.languages = {
            '0x419': "ru-RU",
            '0x409': "en-US",
        }
        self.languages_for_speacher_service = {
            '0x419': "ru",
            '0x409': "en-US",
        }

    def getStr(self, str):
        match self.case:
            case 0:
                return str
            case 1:
                return self.camel_case(str)
            case 2:
                return self.to_snake_case(str)
        return str

    def camel_case(self, s):
        s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join([s[0].lower(), s[1:]])

    def to_snake_case(name, s):
        s = re.sub(' +', '_', s)
        return s.lower()

    def get_keyboard_language(self):
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


def get_keyboard_language():
    languages = {
        '0x419': "ru-RU",
        '0x409': "en-US",
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
