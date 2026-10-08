def estimate_distance(box_height, image_height):

    ratio = box_height / image_height

    if ratio >= 0.60:
        return "Very Close"

    elif ratio >= 0.35:
        return "Close"

    elif ratio >= 0.18:
        return "Medium"

    return "Far"