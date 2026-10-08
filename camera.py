import cv2
import os
import time
import threading

from pynput import keyboard

from services.scene_analyzer import analyze_scene
from services.shared_scene import shared_scene
from services.text_reader import read_text
from services.speech import speak
from services.gemini_service import describe_scene


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "uploads"

LIVE_FRAME_PATH = os.path.join(
    UPLOAD_FOLDER,
    "live_frame.jpg"
)

# Time allowed between Space presses
MULTI_PRESS_WINDOW = 0.7

# Hold duration for exit
HOLD_DURATION = 5.0


# ============================================================
# SETUP
# ============================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

print("=" * 50)
print("          SPATIAL SCENE NARRATOR")
print("=" * 50)
print()
print("Starting camera...")
print()


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)

if not cap.isOpened():

    print("Could not open webcam.")

    raise SystemExit(1)


# ============================================================
# GLOBAL STATE
# ============================================================

running = True


# ------------------------------------------------------------
# Feature processing state
# ------------------------------------------------------------

processing = False

processing_lock = threading.Lock()

current_feature = None


# ------------------------------------------------------------
# Latest camera frame
# ------------------------------------------------------------

latest_frame = None

frame_lock = threading.Lock()


# ------------------------------------------------------------
# Multi-press state
# ------------------------------------------------------------

press_count = 0

press_lock = threading.Lock()

last_press_time = 0


# ------------------------------------------------------------
# Spacebar hold state
# ------------------------------------------------------------

space_pressed = False

space_press_start = None

hold_triggered = False


# ============================================================
# SPEAK HELPER
# ============================================================

def speak_message(message):
    """
    Safely speak a short system/status message.
    """

    if not message:
        return

    try:

        speak(message)

    except Exception as e:

        print(
            "\nSpeech notification error:"
        )

        print(e)


# ============================================================
# FEATURE STATE HELPERS
# ============================================================

def start_feature(feature_name):
    """
    Try to start a feature.

    Returns:
        True  -> feature can start
        False -> another feature is already running
    """

    global processing
    global current_feature

    with processing_lock:

        if processing:

            active_feature = (
                current_feature
                or "another feature"
            )

            print(
                f"\n{feature_name} requested, "
                f"but {active_feature} is already running."
            )

            speak_message(
                f"{active_feature} is already running. "
                f"Please wait until it finishes."
            )

            return False

        processing = True

        current_feature = feature_name

        print(
            f"\n{feature_name} started."
        )

        speak_message(
            f"{feature_name} started."
        )

        return True


def finish_feature(feature_name):
    """
    Mark the feature as finished and inform the user.
    """

    global processing
    global current_feature

    with processing_lock:

        processing = False

        current_feature = None

    print(
        f"\n{feature_name} finished."
    )

    speak_message(
        f"{feature_name} finished. "
        f"You can proceed to the next feature."
    )


def fail_feature(feature_name):
    """
    Mark a feature as finished after an error.
    """

    global processing
    global current_feature

    with processing_lock:

        processing = False

        current_feature = None

    print(
        f"\n{feature_name} could not be completed."
    )

    speak_message(
        f"{feature_name} could not be completed. "
        f"You can try again."
    )


# ============================================================
# FRAME MANAGEMENT
# ============================================================

def get_latest_frame():
    """
    Return a safe copy of the latest webcam frame.
    """

    with frame_lock:

        if latest_frame is None:

            return None

        return latest_frame.copy()


def save_current_frame(frame):
    """
    Save the current webcam frame.
    """

    if frame is None:

        print(
            "No camera frame available."
        )

        return None

    try:

        success = cv2.imwrite(
            LIVE_FRAME_PATH,
            frame
        )

        if not success:

            print(
                "Could not save camera frame."
            )

            return None

        return LIVE_FRAME_PATH

    except Exception as e:

        print(
            "\nFrame Save Error:"
        )

        print(e)

        return None


# ============================================================
# 1 PRESS
# OBJECT + SCENE ANALYSIS
# ============================================================

def analyze_current_frame(frame):

    feature_name = (
        "Object and scene analysis"
    )

    if not start_feature(
        feature_name
    ):

        return

    try:

        print()

        print("=" * 45)

        print(
            "      OBJECT + SCENE ANALYSIS"
        )

        print("=" * 45)

        image_path = save_current_frame(
            frame
        )

        if image_path is None:

            fail_feature(
                feature_name
            )

            return

        print(
            "\nRunning YOLO + Florence..."
        )

        result = analyze_scene(
            image_path
        )

        print()

        print(
            "Scene analysis completed."
        )

        if result:

            print()

            print(
                "Result:"
            )

            print(
                "------------------------------------------"
            )

            print(
                result
            )

            print(
                "------------------------------------------"
            )

        # analyze_scene already speaks the actual
        # scene description.

        finish_feature(
            feature_name
        )

    except Exception as e:

        print()

        print(
            "Scene Analysis Error:"
        )

        print(e)

        fail_feature(
            feature_name
        )


# ============================================================
# 2 PRESSES
# TEXT READER / OCR
# ============================================================

def read_text_from_frame(frame):

    feature_name = (
        "Text reader"
    )

    if not start_feature(
        feature_name
    ):

        return

    try:

        print()

        print("=" * 45)

        print(
            "             TEXT READER"
        )

        print("=" * 45)

        image_path = save_current_frame(
            frame
        )

        if image_path is None:

            fail_feature(
                feature_name
            )

            return

        print(
            "\nRunning Tesseract OCR..."
        )

        text = read_text(
            image_path
        )

        if text:

            print()

            print(
                "Detected text:"
            )

            print(
                "------------------------------------------"
            )

            print(
                text
            )

            print(
                "------------------------------------------"
            )

            # The OCR service may already speak the
            # detected text depending on its implementation.

        else:

            print(
                "\nNo readable text detected."
            )

            speak_message(
                "No readable text detected."
            )

        finish_feature(
            feature_name
        )

    except Exception as e:

        print()

        print(
            "Text Reader Error:"
        )

        print(e)

        fail_feature(
            feature_name
        )


# ============================================================
# 3 PRESSES
# GEMINI DETAILED ANALYSIS
# ============================================================

def gemini_detailed_analysis(frame):

    feature_name = (
        "Gemini detailed analysis"
    )

    if not start_feature(
        feature_name
    ):

        return

    try:

        print()

        print("=" * 45)

        print(
            "       GEMINI DETAILED ANALYSIS"
        )

        print("=" * 45)

        # ----------------------------------------------------
        # Save the current camera frame
        # ----------------------------------------------------

        image_path = save_current_frame(
            frame
        )

        if image_path is None:

            fail_feature(
                feature_name
            )

            return

        print()

        print(
            "Sending current frame to Gemini..."
        )

        print(
            "Image:"
        )

        print(
            image_path
        )

        # ----------------------------------------------------
        # Send image to the existing Gemini service
        # ----------------------------------------------------

        result = describe_scene(
            image_path
        )

        # ----------------------------------------------------
        # Display Gemini response
        # ----------------------------------------------------

        print()

        print(
            "Gemini response:"
        )

        print(
            "------------------------------------------"
        )

        if result:

            print(
                result
            )

        else:

            print(
                "Gemini returned an empty response."
            )

        print(
            "------------------------------------------"
        )

        # ----------------------------------------------------
        # Speak Gemini response
        # ----------------------------------------------------

        if result:

            print(
                "\nSpeaking Gemini description..."
            )

            speak_message(
                result
            )

        else:

            speak_message(
                "Gemini did not return a description."
            )

        # ----------------------------------------------------
        # Feature completed
        # ----------------------------------------------------

        finish_feature(
            feature_name
        )

    except Exception as e:

        print()

        print(
            "Gemini Analysis Error:"
        )

        print(e)

        fail_feature(
            feature_name
        )


# ============================================================
# EXECUTE SELECTED MODE
# ============================================================

def execute_mode(count):

    global running

    if not running:

        return

    frame = get_latest_frame()

    if frame is None:

        print(
            "\nNo camera frame available."
        )

        speak_message(
            "No camera frame is available."
        )

        return

    # --------------------------------------------------------
    # ONE PRESS
    # --------------------------------------------------------

    if count == 1:

        print(
            "\n[1 PRESS DETECTED]"
        )

        print(
            "Object + Scene Analysis"
        )

        threading.Thread(
            target=analyze_current_frame,
            args=(frame,),
            daemon=True
        ).start()

    # --------------------------------------------------------
    # TWO PRESSES
    # --------------------------------------------------------

    elif count == 2:

        print(
            "\n[2 PRESSES DETECTED]"
        )

        print(
            "Text Reader / OCR"
        )

        threading.Thread(
            target=read_text_from_frame,
            args=(frame,),
            daemon=True
        ).start()

    # --------------------------------------------------------
    # THREE PRESSES
    # --------------------------------------------------------

    elif count == 3:

        print(
            "\n[3 PRESSES DETECTED]"
        )

        print(
            "Gemini Detailed Analysis"
        )

        threading.Thread(
            target=gemini_detailed_analysis,
            args=(frame,),
            daemon=True
        ).start()

    else:

        print(
            f"\n{count} presses detected."
        )

        print(
            "Only 1, 2 and 3 presses are supported."
        )

        speak_message(
            "Only one, two, or three presses "
            "are supported."
        )


# ============================================================
# PRESS COUNT PROCESSOR
# ============================================================

def press_processor():

    global press_count
    global last_press_time

    while running:

        time.sleep(
            0.05
        )

        with press_lock:

            if press_count == 0:

                continue

            elapsed = (
                time.time()
                - last_press_time
            )

            if elapsed >= MULTI_PRESS_WINDOW:

                count = press_count

                press_count = 0

            else:

                continue

        execute_mode(
            count
        )


# ============================================================
# KEY PRESS
# ============================================================

def on_key_press(key):

    global running

    global press_count
    global last_press_time

    global space_pressed
    global space_press_start
    global hold_triggered

    if not running:

        return False

    # --------------------------------------------------------
    # SPACEBAR
    # --------------------------------------------------------

    if key == keyboard.Key.space:

        # Ignore repeated key-down events while holding.
        if space_pressed:

            return

        space_pressed = True

        space_press_start = time.time()

        hold_triggered = False

        print(
            "\nSpace pressed..."
        )

        return

    # --------------------------------------------------------
    # Q KEY
    # --------------------------------------------------------

    try:

        if key.char.lower() == "q":

            print(
                "\nQ pressed. Exiting..."
            )

            running = False

            return False

    except AttributeError:

        pass


# ============================================================
# KEY RELEASE
# ============================================================

def on_key_release(key):

    global running

    global press_count
    global last_press_time

    global space_pressed
    global space_press_start
    global hold_triggered

    # --------------------------------------------------------
    # SPACEBAR RELEASE
    # --------------------------------------------------------

    if key == keyboard.Key.space:

        if not space_pressed:

            return

        space_pressed = False

        if space_press_start is None:

            return

        held_time = (
            time.time()
            - space_press_start
        )

        space_press_start = None

        print(
            f"Space released after "
            f"{held_time:.2f} seconds."
        )

        # ----------------------------------------------------
        # LONG HOLD
        # ----------------------------------------------------

        if held_time >= HOLD_DURATION:

            print()

            print(
                "=" * 45
            )

            print(
                "       5 SECOND HOLD DETECTED"
            )

            print(
                "       CLOSING APPLICATION"
            )

            print(
                "=" * 45
            )

            hold_triggered = True

            running = False

            return False

        # ----------------------------------------------------
        # NORMAL PRESS
        # ----------------------------------------------------

        if not hold_triggered:

            with press_lock:

                press_count += 1

                last_press_time = time.time()

                print(
                    f"Press count: {press_count}"
                )


# ============================================================
# START KEYBOARD LISTENER
# ============================================================

keyboard_listener = keyboard.Listener(
    on_press=on_key_press,
    on_release=on_key_release
)

keyboard_listener.start()


# ============================================================
# START PRESS PROCESSOR
# ============================================================

processor_thread = threading.Thread(
    target=press_processor,
    daemon=True
)

processor_thread.start()


# ============================================================
# APPLICATION START MESSAGE
# ============================================================

print()

print(
    "=" * 50
)

print(
    "CONTROLS"
)

print(
    "=" * 50
)

print()

print(
    "SPACE ONCE"
)

print(
    "  -> Object + Scene Analysis"
)

print()

print(
    "SPACE TWICE QUICKLY"
)

print(
    "  -> Text Reader / OCR"
)

print()

print(
    "SPACE THREE TIMES QUICKLY"
)

print(
    "  -> Gemini Detailed Analysis"
)

print()

print(
    "HOLD SPACE FOR 5 SECONDS"
)

print(
    "  -> Exit"
)

print()

print(
    "Q"
)

print(
    "  -> Exit"
)

print()

print(
    "Keyboard listener active."
)

print(
    "You can press Space even if the camera window"
)

print(
    "is not focused."
)

print(
    "=" * 50
)

print()


# ------------------------------------------------------------
# Speak startup message
# ------------------------------------------------------------

speak_message(
    "Spatial Scene Narrator started. "
    "You can press Space to begin."
)


# ============================================================
# MAIN CAMERA LOOP
# ============================================================

try:

    while running:

        ret, frame = cap.read()

        if not ret:

            print(
                "\nCould not read frame from webcam."
            )

            time.sleep(
                0.1
            )

            continue

        # ----------------------------------------------------
        # Store latest frame
        # ----------------------------------------------------

        with frame_lock:

            latest_frame = frame.copy()

        # ----------------------------------------------------
        # Update shared scene
        # ----------------------------------------------------

        shared_scene.update_frame(
            frame
        )

        # ----------------------------------------------------
        # Display camera
        # ----------------------------------------------------

        cv2.imshow(
            "Spatial Scene Narrator",
            frame
        )

        # ----------------------------------------------------
        # OpenCV still needs waitKey so the window updates.
        # Keyboard input itself is handled by pynput.
        # ----------------------------------------------------

        key = cv2.waitKey(
            1
        )

        if key != -1:

            key = key & 0xFF

            if key == ord("q"):

                print(
                    "\nQ pressed. Exiting..."
                )

                running = False

                break


except KeyboardInterrupt:

    print(
        "\nApplication interrupted by user."
    )


finally:

    running = False

    print(
        "\nClosing application..."
    )

    # --------------------------------------------------------
    # Stop keyboard listener
    # --------------------------------------------------------

    try:

        keyboard_listener.stop()

    except Exception:

        pass

    # --------------------------------------------------------
    # Close camera
    # --------------------------------------------------------

    cap.release()

    cv2.destroyAllWindows()

    # --------------------------------------------------------
    # Final spoken notification
    # --------------------------------------------------------

    try:

        speak_message(
            "Application closed."
        )

    except Exception:

        pass

    print(
        "Application Closed Successfully."
    )