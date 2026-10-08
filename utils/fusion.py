def build_scene(objects, scene_description):

    scene = {}

    # Florence description
    scene["description"] = scene_description

    # YOLO detections
    scene["objects"] = objects

    # Nearby obstacles
    scene["near"] = [
        obj for obj in objects
        if obj["distance"] in ("Very Close", "Close")
    ]

    # Left side
    scene["left"] = [
        obj for obj in objects
        if obj["position"] == "Left"
    ]

    # Center
    scene["center"] = [
        obj for obj in objects
        if obj["position"] == "Center"
    ]

    # Right side
    scene["right"] = [
        obj for obj in objects
        if obj["position"] == "Right"
    ]

    # Dangerous objects
    scene["danger"] = [
        obj for obj in objects
        if obj["priority"] >= 2
    ]

    return scene