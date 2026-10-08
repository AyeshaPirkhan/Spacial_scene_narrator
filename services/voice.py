# services/voice.py

import time
import speech_recognition as sr

from services.speech import speaking_event


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()

# Microphone sensitivity
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

# How long the recognizer waits for a pause
recognizer.pause_threshold = 0.55
recognizer.phrase_threshold = 0.2
recognizer.non_speaking_duration = 0.35


# ============================================================
# MICROPHONE
# ============================================================

microphone = None
microphone_ready = False


# ============================================================
# INITIALIZE MICROPHONE
# ============================================================

def initialize_microphone():
    global microphone
    global microphone_ready

    if microphone_ready and microphone is not None:
        return True

    try:
        print("\n====================================")
        print("       INITIALIZING MICROPHONE")
        print("====================================")

        microphone = sr.Microphone()

        with microphone as source:

            print("Adjusting for background noise...")
            print("Please stay quiet for a moment...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

        microphone_ready = True

        print("Microphone ready.")
        print(
            "Energy threshold:",
            recognizer.energy_threshold
        )

        return True

    except Exception as e:

        print("\nMicrophone initialization failed:")
        print(e)

        microphone = None
        microphone_ready = False

        return False


# ============================================================
# LISTEN
# ============================================================

def listen():

    if not initialize_microphone():
        return None

    # --------------------------------------------------------
    # Wait until TTS has finished speaking.
    # --------------------------------------------------------

    while speaking_event.is_set():
        time.sleep(0.1)

    try:

        print("\n------------------------------------")
        print("Listening...")
        print("Speak your command.")
        print("------------------------------------")

        # ----------------------------------------------------
        # Record microphone input.
        # ----------------------------------------------------

        with microphone as source:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

        # ----------------------------------------------------
        # If TTS started while recording, ignore this audio.
        # ----------------------------------------------------

        if speaking_event.is_set():

            print(
                "Speech output started while listening."
            )

            print("Ignoring captured audio.")

            return None

        print("\nProcessing speech...")

        # ----------------------------------------------------
        # Google Speech Recognition
        # ----------------------------------------------------

        command = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        # ----------------------------------------------------
        # Protect against recognition happening while TTS
        # is speaking.
        # ----------------------------------------------------

        if speaking_event.is_set():

            print(
                "Ignoring recognition during speech output."
            )

            return None

        command = command.lower().strip()

        if command:

            print("You said:", command)

            return command

        return None

    except sr.WaitTimeoutError:

        print("No speech detected.")

        return None

    except sr.UnknownValueError:

        print("Could not understand the audio.")

        return None

    except sr.RequestError as e:

        print(
            "Google Speech Recognition Service Error:",
            e
        )

        return None

    except Exception as e:

        print("\nVoice Input Error:")
        print(e)

        return None


# ============================================================
# RESET MICROPHONE
# ============================================================

def reset_microphone():

    global microphone
    global microphone_ready

    microphone = None
    microphone_ready = False

    print("Microphone reset.")