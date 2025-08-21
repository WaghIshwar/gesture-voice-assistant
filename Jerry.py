import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import sys
import time
from os import listdir
from os.path import isfile, join
from pynput.keyboard import Key, Controller
from threading import Thread
import app  # Ensure this connects to eel + GUI frontend

# ---------- Initialization ----------
today = datetime.date.today()
r = sr.Recognizer()
keyboard = Controller()

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

file_exp_status = False
files = []
path = ''
is_awake = True

# ---------- Core Functions ----------
def speak(text):
    print(f"Jerry: {text}")
    app.ChatBot.addAppMsg(text)
    engine.say(text)
    engine.runAndWait()

def wish_user():
    hour = datetime.datetime.now().hour
    greet = "Good Morning!" if hour < 12 else "Good Afternoon!" if hour < 18 else "Good Evening!"
    speak(f"{greet} I am Jerry. How may I help you?")

def record_audio():
    with sr.Microphone() as source:
        r.dynamic_energy_threshold = True
        r.energy_threshold = 300  # Try reducing if it misses input
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 0.8
        r.energy_threshold = 500
        try:
            print("🎙️ Listening...")
            audio = r.listen(source, phrase_time_limit=6)
            voice_data = r.recognize_google(audio).lower()
            print(f"🗣️ You said: {voice_data}")
            return voice_data
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return ""
        except sr.RequestError:
            speak("⚠️ Sorry, my service is down. Please check your internet connection.")
            return ""

def process_command(voice_data):
    global file_exp_status, files, path, is_awake

    voice_data = voice_data.replace("jerry", "").strip()
    app.eel.addUserMsg(voice_data)

    if not voice_data:
        speak("I didn't catch that. Could you repeat?")
        return

    # WAKE UP
    if not is_awake:
        if "wake up" in voice_data:
            is_awake = True
            wish_user()
        return

    # GREETING
    if any(x in voice_data for x in ["hello", "hi", "hey"]):
        wish_user()
        return

    # BASIC COMMANDS
    elif "your name" in voice_data:
        speak("My name is Jerry!")
    elif "date" in voice_data:
        speak(today.strftime("%B %d, %Y"))
    elif "time" in voice_data:
        speak(datetime.datetime.now().strftime("%H:%M:%S"))

    # WEB SEARCH
    if "search" in voice_data:
        query = voice_data.split("search")[-1].strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "location" in voice_data or "map" in voice_data:
        speak("Which location should I look for?")
        location = record_audio()
        if location:
            speak(f"Searching location {location}")
            webbrowser.open(f"https://www.google.com/maps/place/{location}")
        else:
            speak("I couldn't get the location name.")

    elif "open notepad" in voice_data:
        speak("Opening Notepad")
        os.system("notepad.exe")

    elif "open youtube" in voice_data:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open file manager" in voice_data or "open files" in voice_data:
        speak("Opening File Manager")
        os.system("explorer")

    elif "open chrome" in voice_data or "open google chrome" in voice_data:
        speak("Opening Google Chrome")
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if os.path.exists(chrome_path):
            os.startfile(chrome_path)
        else:
            speak("Google Chrome not found on your system.")
    # GOODBYE
    elif "bye" in voice_data:
        speak("Goodbye! Have a nice day.")
        is_awake = False
    elif "exit" in voice_data or "terminate" in voice_data:
        speak("Exiting Jerry. See you next time!")
        app.ChatBot.close()
        sys.exit()

    # SYSTEM COMMANDS
    elif "copy" in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press("c")
            keyboard.release("c")
        speak("Copied")

    elif "paste" in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press("v")
            keyboard.release("v")
        speak("Pasted")

    # FILE EXPLORATION
    elif "list" in voice_data:
        path = "C://"
        try:
            files = listdir(path)
            file_str = "<br>".join(f"{i+1}: {f}" for i, f in enumerate(files))
            app.ChatBot.addAppMsg(file_str)
            speak("Here are the files in the root directory.")
            file_exp_status = True
        except Exception as e:
            speak("Unable to list files.")
            print(e)

    elif file_exp_status:
        if "open" in voice_data:
            try:
                index = int(voice_data.split()[-1]) - 1
                full_path = join(path, files[index])
                if isfile(full_path):
                    os.startfile(full_path)
                    file_exp_status = False
                else:
                    path = join(path, files[index]) + "//"
                    files = listdir(path)
                    file_str = "<br>".join(f"{i+1}: {f}" for i, f in enumerate(files))
                    app.ChatBot.addAppMsg(file_str)
                    speak("Opened folder.")
            except:
                speak("Could not open that file.")
        elif "back" in voice_data:
            if path == "C://":
                speak("Already at root.")
            else:
                path = "//".join(path.strip("//").split("//")[:-1]) + "//"
                files = listdir(path)
                file_str = "<br>".join(f"{i+1}: {f}" for i, f in enumerate(files))
                app.ChatBot.addAppMsg(file_str)
                speak("Went back one level.")
    else:
        speak(f"I heard '{voice_data}', but I'm not trained for that yet.")

# ---------- Main Loop ----------
if __name__ == "__main__":
    Thread(target=app.ChatBot.start).start()
    print("🚀 Jerry is launching...")
    
    while not app.ChatBot.started:
        time.sleep(0.5)

    wish_user()

    while True:
        try:
            user_input = ""
            if app.ChatBot.isUserInput():
                user_input = app.ChatBot.popUserInput().lower()
            else:
                user_input = record_audio()

            if user_input:
                if "jerry" in user_input or app.ChatBot.isUserInput():
                    process_command(user_input)
                if user_input:
                      process_command(user_input)
                else:
                     speak("Please say that again.")

        except SystemExit:
            break
        except Exception as e:
            print(f"🔥 Unhandled exception: {e}")
            speak("Something went wrong.")
