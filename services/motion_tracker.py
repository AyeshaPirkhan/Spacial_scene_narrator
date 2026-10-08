import math

previous_positions = {}


def detect_motion(objects):

    global previous_positions

    events = []

    current_positions = {}

    for obj in objects:

        # Center of bounding box
        center_x = (obj["x1"] + obj["x2"]) // 2
        center_y = (obj["y1"] + obj["y2"]) // 2

        key = (
        obj["name"],
        (obj["x1"] + obj["x2"]) // 2 // 50,
        (obj["y1"] + obj["y2"]) // 2 // 50
        )

        current_positions[key] = (center_x, center_y)

        if key not in previous_positions:
            continue

        old_x, old_y = previous_positions[key]

        movement = math.sqrt(
            (center_x - old_x) ** 2 +
            (center_y - old_y) ** 2
        )

        if movement > 40:

            direction = ""

            if center_x > old_x:
                direction = "towards your right"

            elif center_x < old_x:
                direction = "towards your left"

            else:
                direction = "ahead"

            events.append(
                f"{obj['name'].capitalize()} moving {direction}."
            )

    previous_positions = current_positions

    return events