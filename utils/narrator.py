from collections import defaultdict


def generate_narration(objects):

    grouped = defaultdict(list)

    # Group objects by name
    for obj in objects:
        grouped[obj["name"]].append(
            (obj["position"], obj["distance"])
        )

    narration = []

    for object_name, values in grouped.items():

        for position in ["left", "center", "right"]:

            matching = []

            for pos, dist in values:
                if pos == position:
                    matching.append(dist)

            if len(matching) == 0:
                continue

            count = len(matching)

            # Find the most common distance
            distance = max(set(matching), key=matching.count)

            # Singular / plural
            if count == 1:
                if object_name[0].lower() in "aeiou":
                    sentence = f"There is an {object_name}"
                else:
                    sentence = f"There is a {object_name}"
            else:
                sentence = f"There are {count} {object_name}s"

            # Position
            if position == "left":
                sentence += " on your left"

            elif position == "center":
                sentence += " in front of you"

            else:
                sentence += " on your right"

            # Distance
            if distance == "near":
                sentence += ". It is very close to you."

            elif distance == "medium":
                sentence += ". It is at a moderate distance."

            else:
                sentence += ". It is farther away."

            narration.append(sentence)

    if len(narration) == 0:
        return "No objects detected."

    return " ".join(narration)