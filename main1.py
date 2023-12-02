import speech_recognition as sr
import keyboard

def record_audio():
    # Создание объекта класса Recognizer
    recognizer = sr.Recognizer()

    # Определение источника звука
    # mic_list = sr.Microphone.list_microphone_names()
    # mic_index = mic_list.index("Default")
    # microphone = sr.Microphone(device_index=mic_index)

    # Запись аудио
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Говорите...")
        audio = recognizer.listen(source)

    # Распознавание аудио
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print("Распознанный текст: ", text)
    except sr.UnknownValueError:
        print("Не удалось распознать аудио")
    except sr.RequestError as e:
        print("Ошибка сервиса распознавания речи; {0}".format(e))

# Запуск записи по нажатию на клавишу F1
keyboard.add_hotkey('ctrl+shift+win+f12', record_audio)
keyboard.wait()
