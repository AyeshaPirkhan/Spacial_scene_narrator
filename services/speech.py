# services/speech.py

import threading
import pyttsx3


# Prevent two speech requests from running at the same time.
speech_lock = threading.Lock()

# Lets the voice assistant know when TTS is currently speaking.
speaking_event = threading.Event()


def speak(text):
    """
    Speak the given text using a fresh pyttsx3 engine.

    A new engine is created for every speech request because
    the previous persistent engine was stopping after the
    first speech.
    """

    if not text:
        return

    text = str(text).strip()

    if not text:
        return

    with speech_lock:

        engine = None

        # Tell the voice assistant that speech is active.
        speaking_event.set()

        try:

            print("\nSpeaking:")
            print(text)

            # Create a fresh engine every time.
            engine = pyttsx3.init()

            engine.setProperty("rate", 150)
            engine.setProperty("volume", 1.0)

            voices = engine.getProperty("voices")

            if voices:

                voice_index = 1 if len(voices) > 1 else 0

                engine.setProperty(
                    "voice",
                    voices[voice_index].id
                )

                print(
                    "Using voice:",
                    voices[voice_index].name
                )

            engine.say(text)

            print("Playing speech...")

            engine.runAndWait()

            print("Speech finished.")

        except Exception as e:

            print("\nSpeech Error:")
            print(e)

        finally:

            # Stop and destroy this engine.
            if engine is not None:

                try:
                    engine.stop()

                except Exception:
                    pass

                engine = None

            # Tell the voice assistant speech has finished.
            speaking_event.clear()


def stop_speaking():
    """
    Stop speech if possible.
    """

    print("Stop speech requested.")

    speaking_event.clear()


def shutdown_speech():
    """
    Shut down the speech system.
    """

    speaking_event.clear()

    print("Speech system shut down.")