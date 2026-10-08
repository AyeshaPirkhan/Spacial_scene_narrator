import pyttsx3

print("Initializing TTS...")

engine = pyttsx3.init()

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

print("\nAvailable voices:")

for i, voice in enumerate(voices):
    print(i, voice.name, voice.id)

print("\nSpeaking now...")

engine.say("Hello. This is a test of Windows text to speech.")
engine.runAndWait()

print("\nSpeech finished.")