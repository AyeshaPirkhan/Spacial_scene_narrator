class ObjectTracker:

    def __init__(self):

        self.previous_objects = {}

    def update(self, objects):

        new_objects = []

        current = {}

        for obj in objects:

            key = (
                obj["name"],
                obj["position"]
            )

            current[key] = obj

            if key not in self.previous_objects:
                new_objects.append(obj)

        self.previous_objects = current

        return new_objects


tracker = ObjectTracker()