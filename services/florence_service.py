from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch

# --------------------------------
# Device
# --------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading Florence-2... (first run may take a few minutes)")

# --------------------------------
# Load Model
# --------------------------------
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True
).to(device)

processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True
)

print("Florence-2 Loaded Successfully!")


def describe_scene(image_path):

    image = Image.open(image_path).convert("RGB")

    # Florence task token
    prompt = "<MORE_DETAILED_CAPTION>"

    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(device)

    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=60,
        do_sample=False
    )

    generated_text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    # Remove Florence task token
    generated_text = generated_text.replace(
        "<MORE_DETAILED_CAPTION>",
        ""
    ).strip()

    # Remove duplicated spaces
    generated_text = " ".join(generated_text.split())

    return generated_text