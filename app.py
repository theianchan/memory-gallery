from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import anthropic
import os
import logging
import requests
import random
import ast
from io import BytesIO
from PIL import Image
import time
import uuid

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
phone_number = os.getenv("PHONE_NUMBER")
stability_api_key = os.getenv("STABILITY_API_KEY")

client = anthropic.Anthropic(api_key=anthropic_api_key)

memories = []


def send_generation_request(prompt, negative_prompt=""):
    host = "https://api.stability.ai/v2beta/stable-image/control/style"
    headers = {"Accept": "image/*", "Authorization": f"Bearer {stability_api_key}"}

    references = ['amber.jpg', 'blind.jpg', 'fake.jpg', 'frank.jpg', 'wrong.jpg', 'zouk.jpg']
    reference_image = random.choice(references)
    image_path = os.path.join("static", "images", "gallery", reference_image)

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
        filepath = os.path.join("static", "images", "generated", filename)
        image.save(filepath)
        return filename
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None


def get_image_prompts(message):
    prompt = f"""We're working on an art installation about memory. 
    We want to take a single, user-submitted memory and have an image
    generator (Stable Diffusion) create 4 versions of it. 
    
    1 version should be as close to the original as possible, while 
    the other 3 should contain notable deviations without losing the
    original completely. 

    Please generate 4 image prompts based on this user-submitted message: 
    ```
    {message}
    ```

    The user was asked to submit a memory as their message. They may or 
    may not have done so, since we cannot control user input. Do your best 
    to generate 4 prompts that will result in evocative, stylized 'memories'.
    
    For each prompt:

    - Start with "Detailed painting of" for stylistic consistency
    - Make sure every prompt includes at least one person, but you can include more
    - Include a different 'camera angle' ie. wide shot, close up, top down, etc
    - Include a different lighting instruction ie. "blue-lit scene", 
    "yellow sunlight" etc

    Send each prompt as a element in a python list, for example:
    ```
    ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
    ```

    DO NOT INCLUDE ANYTHING IN YOUR RESPONSE OTHER THAN THE LIST.
    Your response will be consumed by a pipeline, and deviating 
    from the list format will break the pipeline.
    """

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        logging.debug(f"Claude prompted: {prompt}")
        return response.content[0].text.strip('"')
    except Exception as e:
        logging.error(f"Error getting Claude response: {e}")
        return "Unable to generate description at this time."


@app.route("/")
def home():
    return render_template(
        "index.html",
        phone_number=phone_number,
        memories=memories,
    )


@app.route("/memories")
def get_memories():
    logging.debug(f"Returning memories: {memories}")
    return jsonify(memories)


@app.route("/sms", methods=["POST"])
def sms_reply():
    message_body = request.form["Body"]
    logging.debug(f"Text received: {message_body}")

    prompts = get_image_prompts(message_body)
    logging.debug(f"Claude responded: {prompts}")

    prompts = ast.literal_eval(prompts)

    for prompt in prompts:
        image_filename = generate_and_save_image(prompt)
        memories.append(
            {
                "prompt": prompt,
                "image_filename": image_filename,
            }
        )

    logging.debug(f"Memories after append: {memories}")

    return "Successfully received", 200


if __name__ == "__main__":
    os.makedirs(os.path.join("static", "images", "generated"), exist_ok=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
