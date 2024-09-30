from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import anthropic
import os
import logging
import requests
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

messages = []


def send_generation_request(prompt, negative_prompt=""):
    host = "https://api.stability.ai/v2beta/stable-image/control/style"
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {stability_api_key}"
    }

    params = {
        'fidelity': (None, '0.5'),
        'image': os.path.join("static", "images", "reference", "style-all.jpg"),
        'seed': (None, '0'),
        'output_format': (None, 'png'),
        'prompt': (None, prompt),
        'negative_prompt': (None, negative_prompt),
        'aspect_ratio': (None, '16:9')
    }

    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files)==0:
        files["none"] = ''

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
        filepath = os.path.join("static", "generated_images", filename)
        image.save(filepath)
        return filename
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None


def get_claude_response(message):
    prompt = f"""Generate a short, creative description 
        for an art piece based on this message: '{message}'. 
        Keep it under 50 words."""
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
        messages=messages,
    )


@app.route("/messages")
def get_messages():
    logging.debug(f"Returning messages: {messages}")
    return jsonify(messages)


@app.route("/sms", methods=["POST"])
def sms_reply():
    message_body = request.form["Body"]
    logging.debug(f"Text received: {message_body}")

    claude_response = get_claude_response(message_body)
    logging.debug(f"Claude responded: {claude_response}")

    image_filename = generate_and_save_image(claude_response)

    messages.append(
        {
            "message": message_body,
            "claude_response": claude_response,
            "image_filename": image_filename,
        }
    )

    logging.debug(f"Messages after append: {messages}")

    return "Successfully received", 200


if __name__ == "__main__":
    os.makedirs(os.path.join("static", "generated_images"), exist_ok=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
