# services/voice_assistant.py

import threading

from services.shared_scene import shared_scene
from services.voice import listen
from services.command_processor import process_command


def voice_loop():
    """Continuously listen for and process voice commands."""

    print("Voice assistant listening loop started.")

    while True:

        try:
            # ---------------------------------
            # Listen for command
            # ---------------------------------
            command = listen()

            # Ignore empty or unrecognized speech.
            if not command:
                continue

            command = command.strip().lower()

            if not command:
                continue

            print(
                f"\nVoice command received: {command}"
            )

            # ---------------------------------
            # Get latest scene information
            # ---------------------------------
            objects = shared_scene.get_objects()
            description = shared_scene.get_description()

            # ---------------------------------
            # Process command
            # ---------------------------------
            result = process_command(
                command,
                objects,
                description
            )

            # ---------------------------------
            # Exit
            # ---------------------------------
            if result == "EXIT":

                print(
                    "Voice assistant stopped."
                )

                break

        except Exception as e:

            print(
                "\nVoice Assistant Error:"
            )

            print(e)


def start_voice_assistant():
    """Start the voice assistant in a background thread."""

    thread = threading.Thread(
        target=voice_loop,
        daemon=True,
        name="VoiceAssistantThread"
    )

    thread.start()

    print("Voice Assistant Started")