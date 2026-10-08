def get_position(x1, x2, image_width):

    center = (x1 + x2) / 2

    if center < image_width / 3:
        return "Left"

    elif center < (2 * image_width) / 3:
        return "Center"

    return "Right"