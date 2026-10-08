from services.shared_scene import shared_scene
from services.detector import detect_objects
from services.florence_service import describe_scene
from services.reasoning import generate_reasoning
from services.motion_tracker import detect_motion
from services.navigation import generate_navigation
from services.speech import speak

from utils.fusion import build_scene


# ============================================================
# MESSAGE CLEANING
# ============================================================

def clean_message(message):
    """
    Clean and validate a generated message before it is
    returned or spoken.

    Prevents:
    - None values
    - empty messages
    - unfinished fragments
    - excessive whitespace
    - malformed sentence endings
    """

    if message is None:
        return ""

    try:
        message = str(message).strip()
    except Exception:
        return ""

    if not message:
        return ""

    # --------------------------------------------------------
    # Remove common invalid values
    # --------------------------------------------------------

    invalid_values = {
        "none",
        "null",
        "nan",
        "n/a"
    }

    if message.lower() in invalid_values:
        return ""

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    message = " ".join(
        message.split()
    ).strip()

    if not message:
        return ""

    # --------------------------------------------------------
    # Remove accidental repeated punctuation
    # --------------------------------------------------------

    while "  " in message:
        message = message.replace(
            "  ",
            " "
        )

    # --------------------------------------------------------
    # Make sure the message ends as a complete sentence.
    #
    # Do not add punctuation if the generated message already
    # ends with normal sentence punctuation.
    # --------------------------------------------------------

    if message[-1] not in ".!?":

        message += "."

    return message


# ============================================================
# COMBINE GENERATED MESSAGES SAFELY
# ============================================================

def combine_messages(*messages):
    """
    Combine multiple generated messages into one clean,
    grammatically safe spoken message.

    Empty or invalid messages are ignored.
    """

    valid_messages = []

    for message in messages:

        cleaned = clean_message(
            message
        )

        if cleaned:
            valid_messages.append(
                cleaned
            )

    if not valid_messages:
        return ""

    return " ".join(
        valid_messages
    )


# ============================================================
# SCENE ANALYSIS
# ============================================================

def analyze_scene(image_path, speak_result=True):

    print("\nAnalyzing Scene...\n")

    try:

        # ====================================================
        # 1. OBJECT DETECTION
        # ====================================================

        objects = detect_objects(
            image_path
        )

        if objects is None:
            objects = []

        # ====================================================
        # 2. FLORENCE SCENE DESCRIPTION
        # ====================================================

        scene_description = describe_scene(
            image_path
        )

        scene_description = clean_message(
            scene_description
        )

        # ====================================================
        # 3. MOTION DETECTION
        # ====================================================

        motion_events = detect_motion(
            objects
        )

        if motion_events is None:
            motion_events = []

        # ====================================================
        # 4. BUILD COMBINED SCENE
        # ====================================================

        scene = build_scene(
            objects,
            scene_description
        )

        if scene is None:
            scene = {}

        scene["motion"] = motion_events

        # ====================================================
        # 5. GENERATE SCENE REASONING
        # ====================================================

        scene_message = generate_reasoning(
            scene
        )

        scene_message = clean_message(
            scene_message
        )

        # ====================================================
        # 6. GENERATE NAVIGATION ADVICE
        # ====================================================

        navigation_message = generate_navigation(
            scene_description,
            objects
        )

        navigation_message = clean_message(
            navigation_message
        )

        # ====================================================
        # 7. CREATE FINAL ASSISTIVE MESSAGE
        # ====================================================

        final_message = combine_messages(
            scene_message,
            navigation_message
        )

        # ====================================================
        # 8. FALLBACK IF NO VALID MESSAGE WAS GENERATED
        # ====================================================

        if not final_message:

            if objects:

                final_message = (
                    "I detected some objects in the scene, "
                    "but I could not generate a complete "
                    "description. Please proceed carefully."
                )

            else:

                final_message = (
                    "I could not determine the scene clearly. "
                    "Please proceed carefully."
                )

        # Final safety cleanup
        final_message = clean_message(
            final_message
        )

        # ====================================================
        # 9. UPDATE SHARED SCENE
        # ====================================================

        shared_scene.update(
            objects,
            final_message
        )

        # ====================================================
        # 10. PRINT DETECTION RESULTS
        # ====================================================

        print("\nScene Updated:")

        for obj in objects:

            print(
                obj.get(
                    "name",
                    "unknown"
                ),
                obj.get(
                    "position",
                    "unknown"
                ),
                obj.get(
                    "distance",
                    "unknown"
                ),
                obj.get(
                    "confidence",
                    "unknown"
                )
            )

        # ====================================================
        # 11. PRINT SCENE REASONING
        # ====================================================

        print("\nScene Reasoning:")
        print("---------------------------")

        if scene_message:
            print(scene_message)
        else:
            print(
                "No complete scene reasoning generated."
            )

        # ====================================================
        # 12. PRINT NAVIGATION
        # ====================================================

        print("\nNavigation:")
        print("---------------------------")

        if navigation_message:
            print(navigation_message)
        else:
            print(
                "No additional navigation advice generated."
            )

        # ====================================================
        # 13. PRINT FINAL MESSAGE
        # ====================================================

        print("\n===========================")
        print("FINAL ASSISTIVE MESSAGE")
        print("===========================")
        print(final_message)
        print("===========================\n")

        # ====================================================
        # 14. SPEAK FINAL MESSAGE
        # ====================================================

        if final_message and speak_result:

            print(
                "\nSpeaking scene and navigation..."
            )

            speak(
                final_message
            )

        return final_message

    except Exception as e:

        print("\nScene Analysis Error:")
        print(e)

        error_message = (
            "Sorry, I could not complete "
            "the scene analysis."
        )

        error_message = clean_message(
            error_message
        )

        # Only speak on laptop when requested
        if speak_result:

            speak(
                error_message
            )

        return error_message