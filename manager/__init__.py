import speech_recognition as sr

import speach_manager.speech_service
from speach_manager import error, listner


class Manager():

    def __init__(self):
        global state
        self.logger = error.Logger
        self_listner = 'manager'
        self_listners_list = ['list']

    def proc(self):
         with sr.Microphone() as source:
            r = sr.Recognizer()
            while 1:
                # try:
                    audio_data = r.record(source, duration=5)
                    result = r.recognize_google(audio_data, language=state.get_keyboard_language(), show_all=True)
                    self.spec(result)

                # except sr.UnknownValueError:
                #     self.logger.log("Google Speech Recognition could not understand audio")
                # except sr.RequestError as e:
                #     self.logger.log("Could not request results from Google Speech Recognition service; {0}".format(e))
                # except OSError as e:
                #     self.logger.log("OSError service; {0}".format(e))
                # except TypeError as e:
                #     self.logger.log("TypeError service; {0}".format(e))

    def spec(self, result):
        global state
        str = listner.ListnerManger.get_string(result)
        listner.ListnerManger.is_process(str)