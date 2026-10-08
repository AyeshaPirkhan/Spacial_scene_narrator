# services/navigation.py

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
    "truck",
    "bus",
    "dog",
    "cat",
    "stairs"
}

MIN_NAVIGATION_CONFIDENCE = 0.50

DISTANCE_PRIORITY = {
    "Very Close": 0,
    "Close": 1,
    "Medium": 2,
    "Far": 3
}


def get_navigation_objects(detected_objects):

    navigation_objects = []

    for obj in detected_objects:

        name = obj.get("name", "").lower().strip()
        position = obj.get("position", "Center")
        distance = obj.get("distance", "Far")
        confidence = float(obj.get("confidence", 0.0))

        # Ignore objects that are not useful for navigation
        if name not in DANGEROUS_OBJECTS:
            continue

        # Ignore low-confidence detections
        if confidence < MIN_NAVIGATION_CONFIDENCE:
            continue

        # Far objects are not considered immediate navigation obstacles
        if distance == "Far":
            continue

        navigation_objects.append({
            "name": name,
            "position": position,
            "distance": distance,
            "confidence": confidence,
            "priority": DISTANCE_PRIORITY.get(distance, 3)
        })

    return navigation_objects


def get_closest_obstacle(navigation_objects, position=None):

    candidates = navigation_objects

    if position is not None:
        candidates = [
            obj
            for obj in navigation_objects
            if obj["position"] == position
        ]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda obj: obj["priority"]
    )


def generate_direction(navigation_objects):

    # IMPORTANT:
    # If there are no navigation obstacles,
    # return an empty string instead of saying
    # "The path ahead appears clear."

    if not navigation_objects:
        return ""

    left_blocked = any(
        obj["position"] == "Left"
        for obj in navigation_objects
    )

    center_blocked = any(
        obj["position"] == "Center"
        for obj in navigation_objects
    )

    right_blocked = any(
        obj["position"] == "Right"
        for obj in navigation_objects
    )

    # Obstacle directly ahead
    if center_blocked:

        if not left_blocked and not right_blocked:
            return "The path ahead is blocked. Move slightly to either side."

        if left_blocked and not right_blocked:
            return "The path ahead is blocked. Move slightly to the right."

        if right_blocked and not left_blocked:
            return "The path ahead is blocked. Move slightly to the left."

        return "Obstacles are present ahead and on both sides. Stop and proceed carefully."

    # Obstacle only on left
    if left_blocked and not right_blocked:
        return "Keep slightly to the right to avoid the obstacle."

    # Obstacle only on right
    if right_blocked and not left_blocked:
        return "Keep slightly to the left to avoid the obstacle."

    # Obstacles on both sides
    if left_blocked and right_blocked:
        return "Obstacles are present on both sides. Continue straight carefully."

    return ""


def generate_navigation(scene_description, detected_objects):

    navigation_objects = get_navigation_objects(
        detected_objects
    )

    # If there are no relevant navigation obstacles,
    # navigation should say nothing.
    if not navigation_objects:
        return ""

    navigation_messages = []

    # Check center first
    center_obstacle = get_closest_obstacle(
        navigation_objects,
        "Center"
    )

    if center_obstacle:

        name = center_obstacle["name"]
        distance = center_obstacle["distance"]

        navigation_messages.append(
            f"A {name} is directly ahead and is {distance.lower()}."
        )

    # Check left
    left_obstacle = get_closest_obstacle(
        navigation_objects,
        "Left"
    )

    if left_obstacle:

        name = left_obstacle["name"]
        distance = left_obstacle["distance"]

        navigation_messages.append(
            f"A {name} is nearby to your left."
        )

    # Check right
    right_obstacle = get_closest_obstacle(
        navigation_objects,
        "Right"
    )

    if right_obstacle:

        name = right_obstacle["name"]
        distance = right_obstacle["distance"]

        navigation_messages.append(
            f"A {name} is nearby to your right."
        )

    # Generate movement instruction
    direction = generate_direction(
        navigation_objects
    )

    if direction:
        navigation_messages.append(direction)

    return " ".join(navigation_messages)