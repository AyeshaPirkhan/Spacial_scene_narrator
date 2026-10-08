# services/reasoning.py


# ============================================================
# OBJECTS THAT ARE NOT IMPORTANT ENOUGH TO ANNOUNCE
# ============================================================

IGNORE = {
    "cup",
    "bottle",
    "book",
    "cell phone",
    "remote",
    "mouse",
    "keyboard",
    "spoon",
    "fork",
    "knife",
    "cake"
}


# ============================================================
# CLEAN FLORENCE SCENE DESCRIPTION
# ============================================================

def clean_scene_description(description):
    """
    Clean Florence's generated scene description.

    Removes incomplete final fragments while keeping
    complete sentences.
    """

    if not description:
        return ""

    description = str(
        description
    ).strip()

    if not description:
        return ""

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    description = " ".join(
        description.split()
    )

    # --------------------------------------------------------
    # Split description into sentences
    # --------------------------------------------------------

    sentences = []

    current = ""

    for character in description:

        current += character

        if character in ".!?":

            sentence = current.strip()

            if sentence:

                sentences.append(
                    sentence
                )

            current = ""

    remainder = current.strip()

    # --------------------------------------------------------
    # If there is no punctuation, keep the description.
    # --------------------------------------------------------

    if not sentences:

        return description

    # --------------------------------------------------------
    # Handle incomplete final fragment
    # --------------------------------------------------------

    if remainder:

        words = remainder.split()

        incomplete_starters = {
            "on",
            "and",
            "with",
            "while",
            "where",
            "which",
            "that",
            "the",
            "a",
            "an",
            "there",
            "to",
            "near",
            "beside",
            "next"
        }

        first_word = (
            words[0].lower()
            if words
            else ""
        )

        if (
            len(words) >= 4
            and first_word not in incomplete_starters
        ):

            sentences.append(
                remainder + "."
            )

    # --------------------------------------------------------
    # Return cleaned description
    # --------------------------------------------------------

    return " ".join(
        sentences
    ).strip()


# ============================================================
# DESCRIBE IMPORTANT NEARBY OBJECT
# ============================================================

def describe_nearby_object(obj):
    """
    Convert an important nearby object into a natural
    spoken sentence.
    """

    name = str(
        obj.get(
            "name",
            "object"
        )
    ).strip()

    if not name:

        name = "object"

    position = str(
        obj.get(
            "position",
            ""
        )
    ).strip().lower()

    distance = str(
        obj.get(
            "distance",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # Position phrase
    # --------------------------------------------------------

    if position == "left":

        position_phrase = "to your left"

    elif position == "right":

        position_phrase = "to your right"

    elif position == "center":

        position_phrase = "directly ahead"

    else:

        position_phrase = ""

    # --------------------------------------------------------
    # Distance phrase
    # --------------------------------------------------------

    if distance == "Very Close":

        distance_phrase = "very close"

    elif distance == "Close":

        distance_phrase = "nearby"

    elif distance == "Medium":

        distance_phrase = ""

    else:

        distance_phrase = ""

    # --------------------------------------------------------
    # Build natural sentence
    # --------------------------------------------------------

    if position_phrase and distance_phrase:

        return (
            f"There is a {name} "
            f"{distance_phrase} "
            f"{position_phrase}."
        )

    if position_phrase:

        return (
            f"There is a {name} "
            f"{position_phrase}."
        )

    if distance_phrase:

        return (
            f"There is a {name} "
            f"{distance_phrase}."
        )

    return (
        f"There is a {name}."
    )


# ============================================================
# MAIN SCENE REASONING
# ============================================================

def generate_reasoning(scene):
    """
    Generate the scene description only.

    Navigation instructions are intentionally NOT generated
    here. Navigation is handled separately by navigation.py
    so that the final response does not contain duplicate
    obstacle warnings or movement instructions.
    """

    if not scene:

        return (
            "I could not determine the scene clearly."
        )

    description = scene.get(
        "description",
        ""
    )

    objects = scene.get(
        "objects",
        []
    )

    messages = []

    # ========================================================
    # STEP 1
    # FLORENCE SCENE DESCRIPTION
    # ========================================================

    cleaned_description = clean_scene_description(
        description
    )

    if cleaned_description:

        messages.append(
            cleaned_description
        )

    # ========================================================
    # STEP 2
    # IMPORTANT NEARBY OBJECTS
    # ========================================================

    mentioned = set()

    for obj in scene.get(
        "near",
        []
    ):

        if not obj:
            continue

        name = str(
            obj.get(
                "name",
                ""
            )
        ).strip().lower()

        position = str(
            obj.get(
                "position",
                ""
            )
        ).strip()

        distance = str(
            obj.get(
                "distance",
                ""
            )
        ).strip()

        # ----------------------------------------------------
        # Ignore unimportant objects
        # ----------------------------------------------------

        if name in IGNORE:
            continue

        # ----------------------------------------------------
        # Center objects are generally already covered by
        # the main scene description or navigation system.
        # ----------------------------------------------------

        if position == "Center":
            continue

        # ----------------------------------------------------
        # Only announce genuinely nearby objects.
        # ----------------------------------------------------

        if distance not in (
            "Very Close",
            "Close",
            "Medium"
        ):
            continue

        key = (
            name,
            position
        )

        if key in mentioned:
            continue

        mentioned.add(
            key
        )

        message = describe_nearby_object(
            obj
        )

        if message:

            messages.append(
                message
            )

    # ========================================================
    # STEP 3
    # MOTION INFORMATION
    # ========================================================

    motion_events = scene.get(
        "motion",
        []
    )

    if motion_events:

        for event in motion_events:

            if not event:
                continue

            event = str(
                event
            ).strip()

            if not event:
                continue

            # Make sure motion messages end properly.
            if event[-1] not in ".!?":

                event += "."

            messages.append(
                event
            )

    # ========================================================
    # STEP 4
    # REMOVE EMPTY MESSAGES
    # ========================================================

    messages = [
        message.strip()
        for message in messages
        if message
        and message.strip()
    ]

    # ========================================================
    # STEP 5
    # FINAL SCENE MESSAGE
    # ========================================================

    if not messages:

        return (
            "I could not determine the scene clearly."
        )

    final_message = " ".join(
        messages
    ).strip()

    # ========================================================
    # FINAL PUNCTUATION SAFETY
    # ========================================================

    if final_message:

        if final_message[-1] not in ".!?":

            final_message += "."

    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print(
        "\nGenerated Scene Message:\n"
    )

    print(
        final_message
    )

    return final_message