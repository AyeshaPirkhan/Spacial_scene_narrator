
# services/object_finder.py


# Common names that may refer to the same detected object.
OBJECT_ALIASES = {
    "couch": "sofa",
    "sofa": "sofa",
    "cycle": "bicycle",
    "bike": "bicycle",
    "motorbike": "motorcycle",
    " tv": "tv",
}


def normalize_object_name(name):
    """Normalize an object name for matching."""

    if not isinstance(name, str):
        return ""

    name = " ".join(name.lower().strip().split())

    return OBJECT_ALIASES.get(name, name)


def find_object(target, detected_objects):
    """
    Find an object in the currently detected objects.

    Returns a helpful message if the target is missing or
    the object is not present in the detection results.
    """

    # Handle incomplete voice commands.
    if not isinstance(target, str) or not target.strip():
        return "Which object would you like me to find?"

    target = normalize_object_name(target)

    print("\nSearching:", target)
    print("\nCurrent Objects:")

    if not detected_objects:
        return (
            f"I cannot find the {target} because "
            "there are no detected objects available yet."
        )

    matches = []

    for obj in detected_objects:
        print(obj)

        if not isinstance(obj, dict):
            continue

        name = normalize_object_name(obj.get("name", ""))

        if name == target:
            matches.append(obj)

    if matches:
        # Use the first matching detection.
        obj = matches[0]

        distance = obj.get("distance")
        position = obj.get("position")

        if not distance or not position:
            return (
                f"I detected the {target}, "
                "but I do not have enough location information."
            )

        return (
            f"The {target} is "
            f"{str(distance).lower()} "
            f"on your {str(position).lower()}."
        )

    return (
        f"I cannot currently detect the {target}. "
        "Please move the camera around and try again."
    )