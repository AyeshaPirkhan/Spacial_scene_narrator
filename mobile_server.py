# mobile_server.py

import os
import uuid
import threading

from flask import Flask, request, jsonify

from services.scene_analyzer import analyze_scene
from services.text_reader import read_text
from services.gemini_service import describe_scene


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# MOBILE UPLOAD DIRECTORY
# ============================================================

UPLOAD_FOLDER = "uploads/mobile"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# FEATURE STATE
# ============================================================

feature_running = False
current_feature = None
feature_cancelled = False

# Lock protects the feature state because Flask is threaded.
feature_lock = threading.Lock()


# ============================================================
# START FEATURE
# ============================================================

def start_feature(feature_name):

    global feature_running
    global current_feature
    global feature_cancelled

    with feature_lock:

        if feature_running:

            return False

        feature_running = True
        current_feature = feature_name

        # Every newly started feature begins as active.
        feature_cancelled = False

    print(
        f"\n{feature_name} started."
    )

    return True


# ============================================================
# CHECK WHETHER CURRENT FEATURE WAS CANCELLED
# ============================================================

def is_feature_cancelled():

    with feature_lock:

        return feature_cancelled


# ============================================================
# CANCEL CURRENT FEATURE
# ============================================================

def cancel_current_feature():

    global feature_cancelled

    with feature_lock:

        if not feature_running:

            return None

        feature_cancelled = True

        cancelled_feature = current_feature

    print(
        f"\nCancellation requested for:"
        f" {cancelled_feature}"
    )

    return cancelled_feature


# ============================================================
# FINISH FEATURE
# ============================================================

def finish_feature():

    global feature_running
    global current_feature
    global feature_cancelled

    with feature_lock:

        finished_feature = current_feature

        if finished_feature:

            print(
                f"\n{finished_feature} finished."
            )

        feature_running = False
        current_feature = None

        # Reset cancellation state so the next feature
        # starts cleanly.
        feature_cancelled = False


# ============================================================
# SAVE UPLOADED IMAGE
# ============================================================

def save_uploaded_image():

    if "image" not in request.files:

        return None

    uploaded_file = request.files["image"]

    if not uploaded_file.filename:

        return None

    filename = (
        f"{uuid.uuid4().hex}.jpg"
    )

    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    uploaded_file.save(
        image_path
    )

    print(
        f"\nMobile image saved:"
        f"\n{image_path}"
    )

    return image_path


# ============================================================
# SCENE ANALYSIS
# ============================================================

@app.route(
    "/api/scene",
    methods=["POST"]
)
def mobile_scene():

    feature_name = "Scene Analysis"

    if not start_feature(feature_name):

        with feature_lock:
            busy_feature = current_feature

        return jsonify({
            "success": False,
            "busy": True,
            "feature": busy_feature,
            "message":
                f"{busy_feature} is already running. "
                "Please wait."
        }), 409

    image_path = None

    try:

        # ----------------------------------------------------
        # Check cancellation before receiving/processing image.
        # ----------------------------------------------------

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Scene Analysis was cancelled."
            })

        image_path = save_uploaded_image()

        if image_path is None:

            return jsonify({
                "success": False,
                "feature": feature_name,
                "message":
                    "No image was received."
            }), 400

        # ----------------------------------------------------
        # Check again after image upload.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nScene Analysis cancelled "
                "before processing."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Scene Analysis was cancelled."
            })

        # ----------------------------------------------------
        # Use existing Scene Analysis system.
        #
        # speak_result=False is important because the PHONE
        # will speak the returned result.
        # ----------------------------------------------------

        result = analyze_scene(
            image_path,
            speak_result=False
        )

        # ----------------------------------------------------
        # The analysis function itself is synchronous.
        # Therefore, if cancellation happened while it was
        # processing, we cannot stop the already-running
        # function here.
        #
        # Instead, discard its result.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nScene Analysis result discarded "
                "because the feature was cancelled."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Scene Analysis was cancelled."
            })

        return jsonify({
            "success": True,
            "feature": feature_name,
            "result": result or ""
        })

    except Exception as e:

        print(
            "\nMobile Scene Error:"
        )

        print(e)

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Scene Analysis was cancelled."
            })

        return jsonify({
            "success": False,
            "feature": feature_name,
            "message":
                "Sorry, I could not complete "
                "the scene analysis."
        }), 500

    finally:

        finish_feature()

        if image_path:

            try:

                os.remove(
                    image_path
                )

            except Exception:
                pass


# ============================================================
# OCR / TEXT READER
# ============================================================

@app.route(
    "/api/ocr",
    methods=["POST"]
)
def mobile_ocr():

    feature_name = "Text Reader"

    if not start_feature(feature_name):

        with feature_lock:
            busy_feature = current_feature

        return jsonify({
            "success": False,
            "busy": True,
            "feature": busy_feature,
            "message":
                f"{busy_feature} is already running. "
                "Please wait."
        }), 409

    image_path = None

    try:

        # ----------------------------------------------------
        # Check cancellation before upload.
        # ----------------------------------------------------

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Text Reader was cancelled."
            })

        image_path = save_uploaded_image()

        if image_path is None:

            return jsonify({
                "success": False,
                "feature": feature_name,
                "message":
                    "No image was received."
            }), 400

        # ----------------------------------------------------
        # Check cancellation after upload.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nText Reader cancelled "
                "before processing."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Text Reader was cancelled."
            })

        # ----------------------------------------------------
        # Use existing OCR system.
        #
        # speak_result=False prevents the LAPTOP from
        # speaking the OCR result.
        # ----------------------------------------------------

        result = read_text(
            image_path,
            speak_result=False
        )

        # ----------------------------------------------------
        # Discard OCR result if cancellation happened while
        # OCR was running.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nText Reader result discarded "
                "because the feature was cancelled."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Text Reader was cancelled."
            })

        if result:

            message = (
                "I found the following text. "
                + result
            )

        else:

            message = (
                "I could not find any "
                "readable text."
            )

        return jsonify({
            "success": True,
            "feature": feature_name,
            "result": result or "",
            "message": message
        })

    except Exception as e:

        print(
            "\nMobile OCR Error:"
        )

        print(e)

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Text Reader was cancelled."
            })

        return jsonify({
            "success": False,
            "feature": feature_name,
            "message":
                "Sorry, I could not read the text."
        }), 500

    finally:

        finish_feature()

        if image_path:

            try:

                os.remove(
                    image_path
                )

            except Exception:
                pass


# ============================================================
# GEMINI DETAILED ANALYSIS
# ============================================================

@app.route(
    "/api/gemini",
    methods=["POST"]
)
def mobile_gemini():

    feature_name = "Detailed Analysis"

    if not start_feature(feature_name):

        with feature_lock:
            busy_feature = current_feature

        return jsonify({
            "success": False,
            "busy": True,
            "feature": busy_feature,
            "message":
                f"{busy_feature} is already running. "
                "Please wait."
        }), 409

    image_path = None

    try:

        # ----------------------------------------------------
        # Check cancellation before upload.
        # ----------------------------------------------------

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Detailed Analysis was cancelled."
            })

        image_path = save_uploaded_image()

        if image_path is None:

            return jsonify({
                "success": False,
                "feature": feature_name,
                "message":
                    "No image was received."
            }), 400

        # ----------------------------------------------------
        # Check cancellation after upload.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nDetailed Analysis cancelled "
                "before Gemini processing."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Detailed Analysis was cancelled."
            })

        # ----------------------------------------------------
        # Use existing Gemini service.
        #
        # IMPORTANT:
        #
        # If Gemini is already executing inside the SDK,
        # this Python server cannot forcibly terminate that
        # synchronous SDK call.
        #
        # The cancellation flag allows us to discard the
        # Gemini result when the API call eventually returns.
        # ----------------------------------------------------

        result = describe_scene(
            image_path
        )

        # ----------------------------------------------------
        # Check cancellation AFTER Gemini returns.
        #
        # This prevents a cancelled Gemini response from being
        # sent back to Android.
        # ----------------------------------------------------

        if is_feature_cancelled():

            print(
                "\nGemini result discarded "
                "because the feature was cancelled."
            )

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Detailed Analysis was cancelled."
            })

        if not result:

            result = (
                "Sorry, I could not complete "
                "the detailed analysis."
            )

        return jsonify({
            "success": True,
            "feature": feature_name,
            "result": result
        })

    except Exception as e:

        print(
            "\nMobile Gemini Error:"
        )

        print(e)

        if is_feature_cancelled():

            return jsonify({
                "success": False,
                "cancelled": True,
                "feature": feature_name,
                "message":
                    "Detailed Analysis was cancelled."
            })

        return jsonify({
            "success": False,
            "feature": feature_name,
            "message":
                "Sorry, I could not complete "
                "the detailed analysis."
        }), 500

    finally:

        finish_feature()

        if image_path:

            try:

                os.remove(
                    image_path
                )

            except Exception:
                pass


# ============================================================
# CANCEL CURRENT FEATURE
# ============================================================

@app.route(
    "/api/cancel",
    methods=["POST"]
)
def mobile_cancel():

    cancelled_feature = cancel_current_feature()

    if cancelled_feature is None:

        print(
            "\nCancel requested, "
            "but no feature is running."
        )

        return jsonify({
            "success": False,
            "cancelled": False,
            "message":
                "No feature is currently running."
        }), 400

    print(
        f"\n{cancelled_feature} cancellation "
        f"requested successfully."
    )

    return jsonify({
        "success": True,
        "cancelled": True,
        "feature": cancelled_feature,
        "message":
            f"{cancelled_feature} cancellation "
            "requested."
    })


# ============================================================
# SERVER STATUS
# ============================================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def mobile_status():

    with feature_lock:

        running = feature_running
        feature = current_feature
        cancelled = feature_cancelled

    return jsonify({
        "running": running,
        "feature": feature,
        "cancelled": cancelled
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "     SPATIAL SCENE NARRATOR SERVER"
    )

    print(
        "=========================================="
    )

    print(
        "\nServer starting..."
    )

    print(
        "\nAvailable endpoints:"
    )

    print(
        "POST /api/scene"
    )

    print(
        "POST /api/ocr"
    )

    print(
        "POST /api/gemini"
    )

    print(
        "POST /api/cancel"
    )

    print(
        "GET  /api/status"
    )

    print(
        "\nWaiting for Android phone..."
    )

    print(
        "==========================================\n"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )