import speech_recognition as sr
import os
import webbrowser
import datetime
import pyttsx3
import threading
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key

    class Completion:
        @staticmethod
        def create(model, prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
            # Mock response for demonstration purposes
            return {
                "choices": [
                    {"text": "Listening"}
                ]
            }

    class ChatCompletion:
        @staticmethod
        def create(model, messages):
            # Initial response
            return {
                "choices": [
                    {"message": {"content": " "}}
                ]
            }

# Configure Google Generative AI
genai.configure(api_key="your api key")
genai_model = genai.GenerativeModel('gemini-1.5-flash')

chatStr = ""

# Initialize the Gemini client
gemini_client = GeminiClient(api_key="your api key")

# Global flag to indicate TTS status
tts_active = threading.Event()
exit_event = threading.Event()  # Event to signal exit

def chat(query):
    global chatStr
    print(chatStr)
    chatStr += f"User: {query}\nNexus: "
    response = gemini_client.Completion.create(
        model="gemini-3.5",
        prompt=chatStr,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    reply = response["choices"][0]["text"].strip()
    say(reply)
    chatStr += f"{reply}\n"
    return reply

def generate_text(prompt):
    response = gemini_client.ChatCompletion.create(
        model="gemini-3.5",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    reply = response['choices'][0]['message']['content'].strip()
    say(reply)
    return reply

def ai(prompt):
    text = f"Gemini response for Prompt: {prompt}\n*************************\n\n"
    response = gemini_client.Completion.create(
        model="gemini-3.5",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    text += response["choices"][0]["text"].strip()
    if not os.path.exists("Gemini"):
        os.mkdir("Gemini")

    with open(f"Gemini/{''.join(prompt.split('intelligence')[1:]).strip()}.txt", "w") as f:
        f.write(text)

def say(text):
    global tts_active
    tts_active.set()  # Indicate that TTS is active
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    tts_active.clear()  # Indicate that TTS is no longer active

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        self._master = master
        self._sequence = [ImageTk.PhotoImage(img.convert("RGBA"))  # Ensure image is in RGBA mode
                          for img in ImageSequence.Iterator(Image.open(path))]
        self._image_number = 0
        self._delay = kwargs.pop('delay', 20)  # Adjust delay for smoother animation
        self._animating = True
        super().__init__(master, image=self._sequence[0], *args, **kwargs)
        self._animate()

    def _animate(self):
        if self._animating:
            self._image_number = (self._image_number + 1) % len(self._sequence)
            self.configure(image=self._sequence[self._image_number])
            self._master.after(self._delay, self._animate)

    def pause(self):
        self._animating = False

    def resume(self):
        self._animating = True
        self._animate()

def play_gif():
    root = tk.Tk()
    root.title("Nexus moment")
    root.geometry("800x600")
    gif_label = AnimatedGIF(root, 'LCPT.gif', delay=20)  # Adjust delay for smoother animation
    gif_label.pack(expand=True)

    def monitor_tts():
        if tts_active.is_set():
            gif_label.resume()
        else:
            gif_label.pause()
        if not exit_event.is_set():
            root.after(50, monitor_tts)  # Check TTS status every 50ms
        else:
            root.destroy()  # Close the Tkinter window

    root.after(50, monitor_tts)  # Start the monitoring loop
    root.mainloop()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1  # Adjusted to allow longer pauses
        audio = r.listen(source, timeout=10)  # Adjusted to allow a longer listening time
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            print(e)
            return "Some Error Occurred. Sorry from Nexus"

def answer_question(question):
    if question:
        response = genai_model.generate_content(question)
        answer = response.text.strip()
        return answer
    else:
        return "I did not understand the question. Please try again."

if __name__ == '__main__':
    print('Welcome to Nexus A.I')
    say("Hi, this is Nexus")

    # Start GIF in a separate thread
    gif_thread = threading.Thread(target=play_gif)
    gif_thread.start()

    while True:
        query = takeCommand()

        if "open youtube" in query.lower():
            say("Opening YouTube sir...")
            webbrowser.open("https://www.youtube.com")
        elif "open wikipedia" in query.lower():
            say("Opening Wikipedia sir...")
            webbrowser.open("https://www.wikipedia.com")
        elif "open google" in query.lower():
            say("Opening Google sir...")
            webbrowser.open("https://www.google.com")
        elif "open music" in query.lower():
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            os.system(f"open {musicPath}")
        elif "the time" in query.lower():
            hour = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            say(f"Sir, the time is {hour} hours and {minute} minutes")
        elif "open facetime" in query.lower():
            os.system("open /System/Applications/FaceTime.app")
        elif "open pass" in query.lower():
            os.system("open /Applications/Passky.app")
        elif "using artificial intelligence" in query.lower():
            ai(prompt=query)
        elif "open mail" in query.lower():
            say("Opening Mail sir...")
            webbrowser.open("https://www.gmail.com")
        elif "nexus quit" in query.lower():
            say("Goodbye sir")
            exit_event.set()  # Signal the GIF thread to close the window
            gif_thread.join()  # Ensure the GIF thread exits
            exit()
        elif "reset chat" in query.lower():
            chatStr = ""
        elif "nexus answer this" in query.lower():
            question = query.lower().split("nexus answer this", 1)[1].strip()
            if question:
                answer = answer_question(question)
                say(answer)
            else:
                say("I did not understand the question. Please try again.")
        else:
            chat(query)
