# services/detector.py

import os
import cv2

from ultralytics import YOLOWorld

from utils.object_priority import get_priority
from utils.spatial import get_position
from utils.distance import estimate_distance


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = YOLOWorld(
    "yolov8s-worldv2.pt"
)


# --------------------------------------------------
# OBJECTS TO DETECT
# --------------------------------------------------

IMPORTANT_OBJECTS = [

    # People and furniture
    "person",
    "chair",
    "table",
    "bench",
    "sofa",
    "bed",
    "desk",
    "cabinet",
    "bookshelf",
    "shelf",

    # Doors, passages and stairs
    "door",
    "open doorway",
    "stairs",
    "staircase",
    "handrail",

    # Electrical and household objects
    "electrical outlet",
    "light switch",
    "electrical plug",
    "power strip",
    "lamp",
    "fan",
    "television",
    "refrigerator",

    # Common navigation obstacles
    "box",
    "backpack",
    "suitcase",
    "trash can",
    "bucket",
    "potted plant",

    # Vehicles
    "car",
    "motorcycle",
    "bicycle",
    "bus",
    "truck",

    # Animals
    "dog",
    "cat",
]


model.set_classes(
    IMPORTANT_OBJECTS
)


# --------------------------------------------------
# NORMALIZE DETECTED NAMES
# --------------------------------------------------

NAME_MAP = {
    "sofa": "sofa",
    "electrical outlet": "electrical outlet",
    "open doorway": "door",
    "staircase": "stairs",
}


def normalize_name(name):

    if not isinstance(
        name,
        str
    ):
        return ""

    name = " ".join(
        name.lower().strip().split()
    )

    return NAME_MAP.get(
        name,
        name
    )


# --------------------------------------------------
# CONFIDENCE THRESHOLDS
# --------------------------------------------------
#
# Different objects need different confidence levels.
#
# A false positive for a bottle is annoying.
# A false positive for an animal can be confusing.
# A false positive for a navigation obstacle can be
# dangerous.
#
# These values are intentionally conservative starting
# points. We can tune them after testing real frames.
# --------------------------------------------------

DEFAULT_CONFIDENCE = 0.50

PERSON_CONFIDENCE = 0.45

NAVIGATION_CONFIDENCE = 0.50

ANIMAL_CONFIDENCE = 0.90

VEHICLE_CONFIDENCE = 0.65

SMALL_OBJECT_CONFIDENCE = 0.60


NAVIGATION_OBJECTS = {
    "person",
    "chair",
    "table",
    "bench",
    "sofa",
    "bed",
    "desk",
    "cabinet",
    "bookshelf",
    "shelf",
    "door",
    "stairs",
    "handrail",
    "box",
    "backpack",
    "suitcase",
    "trash can",
    "bucket",
    "potted plant",
}


ANIMAL_OBJECTS = {
    "cat",
    "dog",
}


VEHICLE_OBJECTS = {
    "car",
    "motorcycle",
    "bicycle",
    "bus",
    "truck",
}


SMALL_OBJECTS = {
    "electrical outlet",
    "light switch",
    "electrical plug",
    "power strip",
    "lamp",
    "fan",
    "television",
    "refrigerator",
}


def get_confidence_threshold(
    object_name
):

    if object_name == "person":

        return PERSON_CONFIDENCE

    if object_name in ANIMAL_OBJECTS:

        return ANIMAL_CONFIDENCE

    if object_name in VEHICLE_OBJECTS:

        return VEHICLE_CONFIDENCE

    if object_name in NAVIGATION_OBJECTS:

        return NAVIGATION_CONFIDENCE

    if object_name in SMALL_OBJECTS:

        return SMALL_OBJECT_CONFIDENCE

    return DEFAULT_CONFIDENCE


# --------------------------------------------------
# MINIMUM DETECTION SIZE
# --------------------------------------------------
#
# A tiny bounding box can often represent a weak or
# accidental detection.
#
# This is based on percentage of the complete image,
# rather than fixed pixels, so it works across resolutions.
# --------------------------------------------------

MIN_BOX_AREA_RATIO = 0.002


def is_large_enough(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height
):

    box_width = max(
        0,
        x2 - x1
    )

    box_height = max(
        0,
        y2 - y1
    )

    box_area = (
        box_width
        * box_height
    )

    image_area = (
        image_width
        * image_height
    )

    if image_area <= 0:

        return False

    area_ratio = (
        box_area
        / image_area
    )

    return (
        area_ratio
        >= MIN_BOX_AREA_RATIO
    )


# --------------------------------------------------
# OBJECT DETECTION
# --------------------------------------------------

def detect_objects(
    image_path
):

    print(
        "\nRunning YOLO-World detection..."
    )

    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False
    )

    detected_objects = []

    if not results:

        return detected_objects

    result = results[0]

    image_width = result.orig_shape[1]
    image_height = result.orig_shape[0]

    # --------------------------------------------------
    # SAVE ANNOTATED IMAGE
    # --------------------------------------------------

    annotated_image = result.plot()

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    cv2.imwrite(
        "outputs/detected_image.jpg",
        annotated_image
    )

    # --------------------------------------------------
    # PROCESS DETECTIONS
    # --------------------------------------------------

    if result.boxes is not None:

        for box in result.boxes:

            confidence = float(
                box.conf[0]
            )

            class_id = int(
                box.cls[0]
            )

            object_name = result.names[
                class_id
            ]

            object_name = normalize_name(
                object_name
            )

            if not object_name:

                continue

            # --------------------------------------------------
            # CLASS-SPECIFIC CONFIDENCE
            # --------------------------------------------------

            required_confidence = (
                get_confidence_threshold(
                    object_name
                )
            )

            if confidence < required_confidence:

                print(
                    f"Ignored low-confidence "
                    f"{object_name}: "
                    f"{confidence:.2f} "
                    f"(required "
                    f"{required_confidence:.2f})"
                )

                continue

            # --------------------------------------------------
            # BOUNDING BOX
            # --------------------------------------------------

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            # --------------------------------------------------
            # SMALL DETECTION FILTER
            # --------------------------------------------------

            if not is_large_enough(
                x1,
                y1,
                x2,
                y2,
                image_width,
                image_height
            ):

                print(
                    f"Ignored tiny detection: "
                    f"{object_name} "
                    f"{confidence:.2f}"
                )

                continue

            # --------------------------------------------------
            # POSITION
            # --------------------------------------------------

            position = get_position(
                x1,
                x2,
                image_width
            )

            # --------------------------------------------------
            # APPROXIMATE DISTANCE
            # --------------------------------------------------

            box_height = (
                y2 - y1
            )

            distance = estimate_distance(
                box_height,
                image_height
            )

            # --------------------------------------------------
            # PRIORITY
            # --------------------------------------------------

            try:

                priority = get_priority(
                    object_name
                )

            except (
                KeyError,
                ValueError,
                TypeError
            ):

                priority = 1

            # --------------------------------------------------
            # STORE OBJECT
            # --------------------------------------------------

            detected_objects.append({

                "name": object_name,

                "priority": priority,

                "confidence": round(
                    confidence,
                    2
                ),

                "position": position,

                "distance": distance,

                "x1": int(x1),

                "y1": int(y1),

                "x2": int(x2),

                "y2": int(y2),

                "image_width": image_width,

                "image_height": image_height

            })

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------
    #
    # Higher priority objects first.
    # If priorities are equal, higher confidence first.
    # --------------------------------------------------

    detected_objects.sort(
        key=lambda obj: (
            obj["priority"],
            obj["confidence"]
        ),
        reverse=True
    )

    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print(
        "\nYOLO-World Detected Objects:"
    )

    if detected_objects:

        for obj in detected_objects:

            print(
                f"{obj['name']} | "
                f"{obj['confidence']} | "
                f"{obj['position']} | "
                f"{obj['distance']}"
            )

    else:

        print(
            "No reliable objects detected."
        )

    return detected_objects