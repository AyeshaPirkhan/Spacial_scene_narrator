from google import genai
from config import GEMINI_API_KEY

import time


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_MODEL = "gemini-3.8-flash"

MAX_RETRIES = 1


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# GEMINI SCENE DESCRIPTION
# ============================================================

def describe_scene(image_path):

    uploaded_file = None

    try:

        # ====================================================
        # UPLOAD IMAGE
        # ====================================================

        print("\nUploading image to Gemini...")

        uploaded_file = client.files.upload(
            file=image_path
        )

        print(
            "Image uploaded successfully."
        )

        # ====================================================
        # PROMPT
        # ====================================================

        prompt = """
You are an AI assistant helping a visually impaired user.

Analyze the provided image carefully and describe only
information that would be useful to the user.

Mention:

- What place or environment this is
- Important objects and people
- The overall layout
- Important obstacles or hazards
- Anything that may affect safe movement
- Anything especially important for a visually impaired person

Prioritize spatial and safety information.

Do not focus on unnecessary visual details such as
clothing, facial appearance, age, or decorative objects
unless they are important to understanding the scene.

Use simple, natural English that can be spoken aloud
by a text-to-speech system.

Keep the response under 80 words.
"""

        # ====================================================
        # GEMINI REQUEST
        # ====================================================

        print(
            "\nSending image to Gemini for analysis..."
        )

        for attempt in range(MAX_RETRIES + 1):

            try:

                if attempt > 0:

                    print(
                        "\nRetrying Gemini request..."
                    )

                    time.sleep(2)

                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[
                        prompt,
                        uploaded_file
                    ]
                )

                # ============================================
                # CHECK RESPONSE
                # ============================================

                if not response:

                    print(
                        "\nGemini returned no response."
                    )

                    return ""

                # ============================================
                # GET RESPONSE TEXT
                # ============================================

                result = response.text

                if not result:

                    print(
                        "\nGemini returned an empty response."
                    )

                    return ""

                result = result.strip()

                # ============================================
                # SUCCESS
                # ============================================

                print(
                    "\nGemini analysis completed."
                )

                print(
                    "\nGemini Response:"
                )

                print(result)

                return result

            # ================================================
            # GEMINI REQUEST ERROR
            # ================================================

            except Exception as e:

                error_text = str(e)

                print(
                    "\nGemini Request Error:"
                )

                print(e)

                # --------------------------------------------
                # TEMPORARY 503 ERROR
                # --------------------------------------------

                if "503" in error_text:

                    if attempt < MAX_RETRIES:

                        print(
                            "\nGemini temporarily unavailable."
                        )

                        print(
                            "A single retry will be attempted."
                        )

                        continue

                    print(
                        "\nGemini is temporarily unavailable "
                        "after the retry."
                    )

                    print(
                        "Detailed analysis could not be completed."
                    )

                    return ""

                # --------------------------------------------
                # OTHER ERROR
                # --------------------------------------------

                print(
                    "\nGemini analysis failed."
                )

                return ""

        return ""

    # ========================================================
    # GENERAL GEMINI SERVICE ERROR
    # ========================================================

    except Exception as e:

        print(
            "\nGemini Service Error:"
        )

        print(e)

        error_text = str(e)

        if "503" in error_text:

            print(
                "\nGemini is temporarily unavailable "
                "because the model is experiencing "
                "high demand."
            )

        return ""

    # ========================================================
    # CLEANUP
    # ========================================================

    finally:

        uploaded_file = None