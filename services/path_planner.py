# services/path_planner.py

DANGEROUS_OBJECTS = {
    "person",
    "chair",
    "table",
    "bench",
    "couch",
    "sofa",
    "bed",
    "bicycle",
    "motorcycle",
    "car",
    "dog",
    "cat",
    "refrigerator",
    "tv",
    "potted plant"
}


def calculate_score(obstacles):

    score = 0

    for obj in obstacles:

        if obj["distance"] == "Very Close":
            score += 5

        elif obj["distance"] == "Close":
            score += 3

        elif obj["distance"] == "Medium":
            score += 1

    return score


def get_navigation_instruction(objects):

    left = []
    center = []
    right = []

    for obj in objects:

        if obj["name"] not in DANGEROUS_OBJECTS:
            continue

        if obj["position"] == "Left":
            left.append(obj)

        elif obj["position"] == "Center":
            center.append(obj)

        else:
            right.append(obj)

    left_score = calculate_score(left)
    center_score = calculate_score(center)
    right_score = calculate_score(right)

    # --------------------------------------------------
    # Obstacle directly ahead
    # --------------------------------------------------

    if center_score > 0:

        if left_score < right_score:
            return "Obstacle directly ahead. Move slightly left."

        elif right_score < left_score:
            return "Obstacle directly ahead. Move slightly right."

        else:
            return "Obstacle directly ahead. Stop and proceed carefully."

    # --------------------------------------------------
    # Side obstacles
    # --------------------------------------------------

    if left_score > 0 and right_score == 0:
        return "Obstacle on the left. Keep right."

    if right_score > 0 and left_score == 0:
        return "Obstacle on the right. Keep left."

    if left_score > 0 and right_score > 0:

        if left_score < right_score:
            return "Obstacles on both sides. Stay closer to the left."

        elif right_score < left_score:
            return "Obstacles on both sides. Stay closer to the right."

        else:
            return "Obstacles on both sides. Walk slowly."

    return "The path ahead appears clear."