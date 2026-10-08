import time


class SpeechMemory:

    def __init__(self):

        # Last message spoken
        self.last_message = ""

        # Time when it was last spoken
        self.last_time = 0

        # Repeat same message after these many seconds
        self.repeat_after = 6

    def should_speak(self, message):

        now = time.time()

        # First message
        if self.last_message == "":
            self.last_message = message
            self.last_time = now
            return True

        # Message changed
        if message != self.last_message:
            self.last_message = message
            self.last_time = now
            return True

        # Same message after timeout
        if now - self.last_time >= self.repeat_after:
            self.last_time = now
            return True

        return False

    def reset(self):
        """
        Clears speech history.
        Useful when restarting narration.
        """
        self.last_message = ""
        self.last_time = 0


speech_memory = SpeechMemory()