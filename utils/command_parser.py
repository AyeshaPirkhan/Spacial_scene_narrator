
# utils/command_parser.py

import re


# Words and phrases that users may say when naming an object.
OBJECT_ALIASES = {
    "out": "electrical outlet",
    "outlet": "electrical outlet",
    "electrical out": "electrical outlet",
    "plug": "electrical plug",
    "socket": "electrical outlet",
    "switch": "light switch",
    "shelf": "shelf",
    "bookshelf": "bookshelf",
    "couch": "sofa",
    "sofa": "sofa",
    "bed": "bed",
    "chair": "chair",
    "table": "table",
    "desk": "desk",
    "person": "person",
    "people": "person",
    "man": "person",
    "woman": "person",
    "cat": "cat",
    "dog": "dog",
    "door": "door",
    "stairs": "stairs",
    "stair": "stairs",
    "car": "car",
    "bike": "bicycle",
    "bicycle": "bicycle",
    "motorbike": "motorcycle",
    "motorcycle": "motorcycle",
    "tv": "television",
    "television": "television",
    "plant": "potted plant",
    "bin": "trash can",
    "trash bin": "trash can",
    "bucket": "bucket",
    "box": "box",
}


def clean_command(command):
    """Normalize speech-recognition text for command matching."""

    if not isinstance(command, str):
        return ""

    command = command.lower().strip()
    command = re.sub(r"[^\w\s'-]", " ", command)
    command = re.sub(r"\s+", " ", command)

    # Remove common hesitation/filler words.
    command = re.sub(
        r"\b(uh|um|please|hey assistant|hey)\b",
        " ",
        command
    )

    return re.sub(r"\s+", " ", command).strip()


def get_command(command):
    """Return the intent: describe, front, find, walk, exit, or unknown."""

    command = clean_command(command)

    if not command:
        return "unknown"

    # Exit commands
    if re.search(
        r"\b(exit|quit|close|shutdown|stop listening)\b",
        command
    ):
        return "exit"

    # Description requests
    describe_phrases = [
        "describe",
        "describe my surroundings",
        "describe my surrounding",
        "surroundings",
        "environment",
        "around me",
        "what do you see",
        "what can you see",
        "tell me what you see",
        "tell me about my surroundings",
        "what is around me",
    ]

    if any(phrase in command for phrase in describe_phrases):
        return "describe"

    # Requests about the area in front of the user
    if any(phrase in command for phrase in [
        "what is in front",
        "what's in front",
        "objects in front",
        "in front of me",
        "directly ahead",
        "what is ahead",
    ]):
        return "front"

    # Navigation / path questions
    if any(phrase in command for phrase in [
        "walk",
        "move",
        "path",
        "safe",
        "which way",
        "which direction",
        "how do i get",
        "can i go",
        "is it safe",
        "guide me",
        "guide",
    ]):
        return "walk"

    # Explicit object-search language
    if any(phrase in command for phrase in [
        "find",
        "where",
        "locate",
        "look for",
        "search for",
        "tell me where",
        "show me",
        "do you see",
        "can you see",
    ]):
        return "find"

    # Standalone object words and recognized partial object names.
    target = get_target_object(command)

    if target:
        return "find"

    return "unknown"


def get_target_object(command):
    """
    Extract an object name from a command.

    Supports direct object words, aliases, and incomplete names.
    Returns None if no object target can be identified.
    """

    command = clean_command(command)

    if not command:
        return None

    # Remove command phrases wherever they occur.
    prefixes = [
        r"^(?:can you|could you|would you)\s+",
        r"^(?:please\s+)?(?:find|locate|search for|look for)\s+",
        r"^(?:where is|where's|where are|where can i find)\s+",
        r"^(?:do you see|can you see)\s+",
        r"^(?:show me|tell me where)\s+",
        r"^(?:tell me about)\s+",
    ]

    changed = True
    while changed:
        changed = False
        for pattern in prefixes:
            updated = re.sub(pattern, "", command).strip()
            if updated != command:
                command = updated
                changed = True

    # Remove common filler words at the beginning and end.
    filler_words = {
        "the", "a", "an", "my", "me", "please",
        "is", "are", "at", "in", "on", "to",
        "for", "there", "located", "right", "now",
        "near", "of",
    }

    words = command.split()

    while words and words[0] in filler_words:
        words.pop(0)

    while words and words[-1] in filler_words:
        words.pop()

    if not words:
        return None

    phrase = " ".join(words)

    # Exact aliases first.
    if phrase in OBJECT_ALIASES:
        return OBJECT_ALIASES[phrase]

    # Allow phrases that end in a known object name, e.g.
    # "the electrical out" -> "electrical outlet".
    for alias in sorted(OBJECT_ALIASES, key=len, reverse=True):
        if phrase.endswith(alias):
            return OBJECT_ALIASES[alias]

    # Handle common incomplete forms of longer object labels.
    partial_aliases = {
        "electrical ou": "electrical outlet",
        "electrical outl": "electrical outlet",
        "electrical outle": "electrical outlet",
        "light swi": "light switch",
        "power": "power strip",
        "book": "bookshelf",
        "shel": "shelf",
        "stairca": "stairs",
        "motor": "motorcycle",
        "bicy": "bicycle",
    }

    if phrase in partial_aliases:
        return partial_aliases[phrase]

    # Return the phrase itself for multi-word explicit search requests.
    # The object finder can then attempt to match it.
    if len(words) > 1:
        return phrase

    # For a single word, allow it as a target only if recognized.
    return None