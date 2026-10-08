import cv2
import pytesseract
import re

from services.speech import speak
from services.ocr_space import extract_text_ocr_space


# ---------------------------------------------------------
# TESSERACT CONFIGURATION
# ---------------------------------------------------------

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

MIN_WORD_CONFIDENCE = 45
RELIABLE_CONFIDENCE = 60

# Maximum time allowed for ONE Tesseract OCR attempt
TESSERACT_TIMEOUT = 10


# ---------------------------------------------------------
# CREATE OCR IMAGE
# ---------------------------------------------------------

def create_ocr_images(image):
    """
    Creates only fast OCR preprocessing variants.

    We intentionally DO NOT use adaptive thresholding because
    it was causing very long processing times on some images.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize moderately for better OCR.
    height, width = gray.shape

    if width < 1200:
        scale = 1200 / width
        new_width = int(width * scale)
        new_height = int(height * scale)

        gray = cv2.resize(
            gray,
            (new_width, new_height),
            interpolation=cv2.INTER_CUBIC
        )

    # Method 1: grayscale
    grayscale = gray

    # Method 2: Otsu threshold
    _, otsu = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return {
        "grayscale": grayscale,
        "otsu": otsu
    }


# ---------------------------------------------------------
# CHECK WHETHER OCR RESULT LOOKS LIKE REAL TEXT
# ---------------------------------------------------------

def looks_like_text(text):
    if not text:
        return False

    text = text.strip()

    if len(text) < 3:
        return False

    # Count alphabetic characters
    letters = len(re.findall(r"[A-Za-z]", text))

    # Count numbers
    numbers = len(re.findall(r"\d", text))

    # Count total meaningful characters
    meaningful = letters + numbers

    if meaningful < 3:
        return False

    return True


# ---------------------------------------------------------
# RUN ONE TESSERACT OCR ATTEMPT
# ---------------------------------------------------------

def run_tesseract(image, method_name):
    """
    Runs one OCR attempt with a strict timeout.

    This prevents Tesseract from hanging indefinitely.
    """

    print(f"\nTrying Tesseract method: {method_name}")

    try:
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config="--psm 6",
            timeout=TESSERACT_TIMEOUT
        )

        words = []
        confidences = []

        for i, word in enumerate(data["text"]):

            word = word.strip()

            if not word:
                continue

            try:
                confidence = float(data["conf"][i])
            except (ValueError, TypeError):
                continue

            if confidence < MIN_WORD_CONFIDENCE:
                continue

            words.append(word)
            confidences.append(confidence)

        if not words:
            print("No reliable words detected.")
            return "", 0.0

        text = " ".join(words)

        average_confidence = sum(confidences) / len(confidences)

        print("Result:")
        print(text)

        print(
            f"Confidence: {average_confidence:.1f}%"
        )

        return text, average_confidence

    except RuntimeError as e:

        # pytesseract timeout raises RuntimeError
        print(
            f"Tesseract {method_name} timed out "
            f"after {TESSERACT_TIMEOUT} seconds."
        )

        return "", 0.0

    except Exception as e:

        print(
            f"Tesseract {method_name} error:"
        )

        print(e)

        return "", 0.0


# ---------------------------------------------------------
# LOCAL TESSERACT OCR
# ---------------------------------------------------------

def extract_text_tesseract(image_path):

    print("\nTrying local Tesseract OCR...")

    image = cv2.imread(image_path)

    if image is None:

        print("Could not open image.")

        return "", 0.0

    ocr_images = create_ocr_images(image)

    best_text = ""
    best_confidence = 0.0
    best_method = ""

    # -----------------------------------------------------
    # METHOD 1 — GRAYSCALE
    # -----------------------------------------------------

    text, confidence = run_tesseract(
        ocr_images["grayscale"],
        "grayscale"
    )

    if confidence > best_confidence:

        best_text = text
        best_confidence = confidence
        best_method = "grayscale"

    # -----------------------------------------------------
    # EARLY EXIT
    # -----------------------------------------------------
    # If grayscale already gives a good result, STOP.
    #
    # This is the major speed improvement.
    # -----------------------------------------------------

    if (
        confidence >= RELIABLE_CONFIDENCE
        and looks_like_text(text)
    ):

        print(
            "\nGrayscale produced a reliable result."
        )

        return best_text, best_confidence

    # -----------------------------------------------------
    # METHOD 2 — OTSU
    # -----------------------------------------------------

    text, confidence = run_tesseract(
        ocr_images["otsu"],
        "otsu"
    )

    if confidence > best_confidence:

        best_text = text
        best_confidence = confidence
        best_method = "otsu"

    # -----------------------------------------------------
    # FINAL LOCAL RESULT
    # -----------------------------------------------------

    if best_text:

        print(
            f"\nSelected Tesseract method: "
            f"{best_method}"
        )

        print(
            f"Tesseract confidence: "
            f"{best_confidence:.1f}%"
        )

    else:

        print(
            "\nTesseract could not detect readable text."
        )

    return best_text, best_confidence


# ---------------------------------------------------------
# MAIN TEXT READER
# ---------------------------------------------------------

def read_text(image_path, speak_result=True):

    print("\n==========================================")
    print("             TEXT READER")
    print("==========================================")

    try:

        # -------------------------------------------------
        # STEP 1 — TESSERACT
        # -------------------------------------------------

        text, confidence = extract_text_tesseract(
            image_path
        )

        # -------------------------------------------------
        # STEP 2 — ACCEPT GOOD TESSERACT RESULT
        # -------------------------------------------------

        if (
            text
            and confidence >= RELIABLE_CONFIDENCE
            and looks_like_text(text)
        ):

            final_text = text

            print("\nOCR Source: Tesseract")

        else:

            # -------------------------------------------------
            # STEP 3 — OCR.SPACE FALLBACK
            # -------------------------------------------------

            print(
                "\nTesseract result was not reliable."
            )

            print(
                "Trying OCR.space fallback..."
            )

            try:

                ocr_space_text = extract_text_ocr_space(
                    image_path
                )

            except Exception as e:

                print(
                    "\nOCR.space Error:"
                )

                print(e)

                ocr_space_text = ""

            if looks_like_text(ocr_space_text):

                final_text = ocr_space_text

                print(
                    "\nOCR Source: OCR.space"
                )

            else:

                final_text = ""

        # -------------------------------------------------
        # STEP 4 — NO TEXT FOUND
        # -------------------------------------------------

        if not final_text:

            print(
                "\nNo readable text was detected."
            )

            if speak_result:

                speak(
                    "I could not find any readable text."
                )

            return ""

        # -------------------------------------------------
        # STEP 5 — DISPLAY RESULT
        # -------------------------------------------------

        print(
            "\nDetected Text:"
        )

        print("------------------------------------------")

        print(final_text)

        print("------------------------------------------")

        # -------------------------------------------------
        # STEP 6 — SPEAK RESULT
        # -------------------------------------------------

        if speak_result:

            speak(
                "I found the following text. "
                + final_text
            )

        print(
            "\nText Reader finished."
        )

        return final_text

    except Exception as e:

        print(
            "\nText Reader Error:"
        )

        print(e)

        if speak_result:

            speak(
                "Sorry, I could not read the text."
            )

        return ""