VERY_HIGH = {
    "person",
    "car",
    "bus",
    "truck",
    "motorcycle",
    "bicycle"
}

HIGH = {
    "chair",
    "table",
    "bench",
    "bed",
    "sofa",
    "couch",
    "dog",
    "cat"
}

MEDIUM = {
    "tv",
    "refrigerator",
    "potted plant",
    "sink",
    "oven",
    "microwave"
}


def get_priority(name):

    if name in VERY_HIGH:
        return 3

    if name in HIGH:
        return 2

    if name in MEDIUM:
        return 1

    return 0