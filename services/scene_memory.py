import time


class SceneMemory:

    def __init__(self):
        self.last_message = ""
        self.last_time = 0

    def self, message):

        current_time = time.time()

        # Different message → speak immediately
        if message != self.last_message:

            self.last_message = message
            self.last_time = current_time
            return True

        # Same message but 5 seconds have passed
        if current_time - self.last_time >= 5:

            self.last_time = current_time
            return True

        return False


memory = SceneMemory()