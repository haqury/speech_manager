import pyperclip as pc
SNAKE_CASE = ['snake', 'make', 'снейк', 'smokies']
CAMEL_CASE = ['camel', 'como', 'кому', 'хаббл', 'kamo']
DEFAULT_CASE = ['default', 'the fault', 'the fall', 'дефолт_кейс', 'стандарт_кейс']
IS_UP = ['is up', 'из opt', 'is app', 'is apt']


class CaseManager:
    def __init__(self, listner_manager):
        self.commands = IS_UP + SNAKE_CASE + CAMEL_CASE + DEFAULT_CASE
        self.listner_manager = listner_manager

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self, str):
        for case in SNAKE_CASE:
            if str.find(case) != -1:
                self.change_case(2)
                return 2

        for case in CAMEL_CASE:
            if str.find(case) != -1:
                self.change_case(1)
                return 1

        for case in DEFAULT_CASE:
            if str.find(case) != -1:
                self.change_case(0)
                return 0

        if str.find('is up') != -1:
            if str.find('true') != -1 \
                    or str.find('through') != -1 \
                    or str.find('.ru')  != -1 \
                    or str.find('room')  != -1 \
                    or str.find('ton')  != -1:
                self.change_uper(True)
            else:
                self.change_uper(False)

    def change_case(self, type):
        self.listner_manager.state.case = type
        self.listner_manager.last_rebuld()

    def change_uper(self, type):
        print('upper case', type)
        self.listner_manager.state.is_up = type
        self.listner_manager.last_rebuld()
