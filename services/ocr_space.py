# services/ocr_space.py

import os
import tempfile

import cv2
import requests

from dotenv import load_dotenv

load_dotenv()

OCR_SPACE_API_KEY = os.getenv(
    "OCR_SPACE_API_KEY"
)

OCR_SPACE_URL = (
    "https://api.ocr.space/parse/image"
)

MAX_FILE_SIZE = 1024 * 1024  # 1 MB


def prepare_image(image_path):
    """
    Prepare an image for OCR.space.

    If the original image is already below the
    1 MB limit, use it directly.

    Otherwise, convert it to a compressed JPEG.
    """

    original_size = os.path.getsize(
        image_path
    )

    print(
        f"\nOriginal image size: "
        f"{original_size} bytes"
    )

    if original_size <= MAX_FILE_SIZE:
        print(
            "Image is within OCR.space size limit."
        )

        return image_path, False

    print(
        "Image is larger than 1 MB."
    )

    print(
        "Compressing image before upload..."
    )

    image = cv2.imread(
        image_path
    )

    if image is None:
        print(
            "Could not read image."
        )

        return None, False

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    temp_path = temp_file.name

    temp_file.close()

    quality = 85

    success = False

    while quality >= 40:

        success = cv2.imwrite(
            temp_path,
            image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                quality
            ]
        )

        if not success:
            break

        compressed_size = os.path.getsize(
            temp_path
        )

        print(
            f"JPEG quality {quality}: "
            f"{compressed_size} bytes"
        )

        if compressed_size <= MAX_FILE_SIZE:
            print(
                "Compressed image is within "
                "OCR.space size limit."
            )

            return temp_path, True

        quality -= 5

    print(
        "Could not compress image below "
        "the 1 MB limit."
    )

    try:
        os.remove(temp_path)
    except OSError:
        pass

    return None, False


def extract_text_ocr_space(image_path):

    if not OCR_SPACE_API_KEY:

        print(
            "\nOCR.space API key not found."
        )

        return "", 0

    if not os.path.exists(image_path):

        print(
            f"\nImage not found: {image_path}"
        )

        return "", 0

    temporary_file = None

    try:

        upload_path, temporary_file = (
            prepare_image(image_path)
        )

        if upload_path is None:

            return "", 0

        if temporary_file:

            print(
                "\nUsing compressed JPEG:"
            )

            print(
                upload_path
            )

        print(
            "\nSending image to OCR.space..."
        )

        headers = {
            "apikey": OCR_SPACE_API_KEY
        }

        file_extension = os.path.splitext(
            upload_path
        )[1].lower()

        if file_extension == ".jpg" or file_extension == ".jpeg":

            mime_type = "image/jpeg"

            file_type = "JPG"

        else:

            mime_type = "image/png"

            file_type = "PNG"

        with open(
            upload_path,
            "rb"
        ) as image_file:

            files = {
                "file": (
                    os.path.basename(
                        upload_path
                    ),
                    image_file,
                    mime_type
                )
            }

            data = {
                "language": "eng",
                "OCREngine": "2",
                "filetype": file_type,
                "isOverlayRequired": "false",
                "detectOrientation": "true",
                "scale": "true",
                "isTable": "false"
            }

            response = requests.post(
                OCR_SPACE_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=90
            )

        print(
            "\nHTTP Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "\nOCR.space HTTP Error:"
            )

            print(
                response.text
            )

            return "", 0

        try:

            result = response.json()

        except ValueError:

            print(
                "\nOCR.space returned "
                "invalid JSON."
            )

            print(
                response.text
            )

            return "", 0

        print(
            "\nOCRExitCode:",
            result.get(
                "OCRExitCode"
            )
        )

        print(
            "IsErroredOnProcessing:",
            result.get(
                "IsErroredOnProcessing"
            )
        )

        if result.get(
            "ErrorMessage"
        ):

            print(
                "\nErrorMessage:"
            )

            print(
                result.get(
                    "ErrorMessage"
                )
            )

        parsed_results = result.get(
            "ParsedResults",
            []
        )

        if not parsed_results:

            print(
                "\nOCR.space returned "
                "no parsed results."
            )

            return "", 0

        detected_text_parts = []

        for index, parsed_result in enumerate(
            parsed_results
        ):

            print(
                f"\nProcessing result "
                f"{index + 1}..."
            )

            parsed_text = parsed_result.get(
                "ParsedText",
                ""
            )

            if parsed_text:

                detected_text_parts.append(
                    parsed_text.strip()
                )

        if not detected_text_parts:

            print(
                "\nNo readable text detected."
            )

            return "", 0

        final_text = "\n".join(
            detected_text_parts
        ).strip()

        print(
            "\nOCR.space Result:"
        )

        print(
            "------------------------------------------"
        )

        print(
            final_text
        )

        print(
            "------------------------------------------"
        )

        return (
            final_text,
            0
        )

    except requests.exceptions.Timeout:

        print(
            "\nOCR.space request timed out."
        )

        return "", 0

    except requests.exceptions.RequestException as e:

        print(
            "\nOCR.space connection error:"
        )

        print(e)

        return "", 0

    except Exception as e:

        print(
            "\nOCR.space error:"
        )

        print(e)

        return "", 0

    finally:

        if temporary_file:

            try:

                os.remove(
                    upload_path
                )

                print(
                    "\nTemporary OCR image "
                    "deleted."
                )

            except OSError:
                pass