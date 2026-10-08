def find_object(objects, target):

    target = target.lower()

    for obj in objects:

        if obj["name"].lower() == target:

            return {
                "found": True,
                "name": obj["name"],
                "position": obj["position"],
                "distance": obj["distance"],
                "confidence": obj["confidence"]
            }

    return {
        "found": False
    }