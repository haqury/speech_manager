#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import time

import speech_recognition as sr

def run(callback):
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

    # start listening in the background (note that we don't have to do this inside a `with` statement)
    stop_listening = r.listen_in_background(m, callback)
    # `stop_listening` is now a function that, when called, stops background listening

    # do some unrelated computations for 5 seconds
    for _ in range(50): time.sleep(0.1)  # we're still listening even though the main thread is doing other things

    # calling this function requests that the background listener stop listening
    stop_listening(wait_for_stop=False)

    # do some more unrelated things
    while True: time.sleep(
        0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping
