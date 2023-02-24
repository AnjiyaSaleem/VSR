from flask import Flask, render_template, request,flash
import azure.cognitiveservices.speech as speechsdk
import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS
from nltk.tokenize import word_tokenize
from datetime import datetime
import pynput
from pynput import keyboard
path = os.getcwd()


speech_key, service_region = "e9866f4cbe0640048a3c0052399e8364", "eastus"
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key, region=service_region)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


app = Flask(__name__)
app.secret_key = "#123%^&"


@app.route("/")
def home():
    return render_template('index.html')

all_results = []
def handle_final_result(evt):
    all_results.append(evt.result.text)


@app.route("/start")
def speak():
    date_string = datetime.now().strftime("%d%m%Y%H%M%S")
    tts = gTTS("Calibrating Microphone ...", lang="en")
    filename = "voice"+date_string+".mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
    get_audio()
    return render_template('index.html')


done = False


def stop_cb(evt):
    print('CLOSING on {}'.format(evt))
    speech_recognizer.stop_continuous_recognition()
    global done
    done = True


@app.route("/stop")
def stopTranscription():
    flash("The audio is processing.");
    speech_recognizer.stop_continuous_recognition()
    print('CLOSING')
    print("Printing all results:")
    print(all_results)

    c = keyboard.Controller()
    for phrase in all_results:
        c.type(phrase)
    all_results.clear() 
    return render_template('index.html')


def get_audio():
    print("Say something...")
    all_results.clear() 
    speech_recognizer.recognized.connect(handle_final_result)
    speech_recognizer.recognized.connect(lambda evt: print(format(evt.result.text)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    flash("The audio is processing.");
    speech_recognizer.start_continuous_recognition()

    return render_template('index.html')


if __name__ == "_main_":
    app.run(debug=True)