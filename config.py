import os

class Config():
    def __init__(self):
        self.Languages = dict()
        self.Languages["ru-RU"] = '0x4090409'
        self.Languages["en-US"] = '0x4190419'

        self.GPT_KEY = os.getenv('GPT_KEY')