
import threading


class SharedScene:

    def __init__(self):
        self.objects = []
        self.description = ""
        self.latest_frame = None
        self.lock = threading.Lock()

    def update(self, objects, description):
        with self.lock:
            self.objects = list(objects)
            self.description = description

    def get_objects(self):
        with self.lock:
            return list(self.objects)

    def get_description(self):
        with self.lock:
            return self.description

    def update_frame(self, frame):
        """Store a copy of the latest webcam frame."""
        if frame is None:
            return

        with self.lock:
            self.latest_frame = frame.copy()

    def get_latest_frame(self):
        """Return a copy so another thread cannot modify the stored frame."""
        with self.lock:
            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()


shared_scene = SharedScene()