import os
import random
import requests
import logging
from PIL import Image
from io import BytesIO
import uuid
from .config import static_dir, STABILITY_API_KEY


def send_generation_request(prompt, negative_prompt=""):
    host = "https://api.stability.ai/v2beta/stable-image/control/style"
    headers = {"Accept": "image/*", "Authorization": f"Bearer {STABILITY_API_KEY}"}

    image_path = random.choice(
        [
            os.path.join(static_dir, "images", "reference", f)
            for f in os.listdir(os.path.join(static_dir, "images", "reference"))
            if f.lower().endswith(".jpg")
        ]
    )

    params = {
        "fidelity": (None, "0.5"),
        "image": image_path,
        "seed": (None, "0"),
        "output_format": (None, "png"),
        "prompt": (None, prompt),
        "negative_prompt": (None, negative_prompt),
        "aspect_ratio": (None, "3:2"),
    }

    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != "":
        files["image"] = open(image, "rb")
    if mask is not None and mask != "":
        files["mask"] = open(mask, "rb")
    if len(files) == 0:
        files["none"] = ""

    logging.debug(
        f"Prompting Stability with image `{image_path}` and prompt `{prompt}`"
    )
    response = requests.post(host, headers=headers, files=files, data=params)

    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response


def generate_and_save_image(prompt):
    try:
        response = send_generation_request(prompt)
        if response.headers.get("finish-reason") == "CONTENT_FILTERED":
            raise Warning("Generation failed NSFW classifier")

        image = Image.open(BytesIO(response.content))
        filename = f"image_{uuid.uuid4()}.png"
        filepath = os.path.join(static_dir, "images", "generated", filename)
        image.save(filepath)
        logging.debug(f"Saved image to `{filepath}`")

        return filename

    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None
