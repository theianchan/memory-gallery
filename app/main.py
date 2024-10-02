from flask import Flask, request, render_template, jsonify
import os
import logging
import ast
from .config import template_dir, static_dir, NUM_MEMORIES, PHONE_NUMBER
from .database import get_db_connection, init_db
from .images import generate_and_save_image
from .prompts import get_image_prompts_captions

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

memories = []


@app.route("/")
def home():
    return render_template(
        "index.html",
        phone_number=PHONE_NUMBER,
        memories=memories,
    )


@app.route("/memories")
def get_memories():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM memories ORDER BY RANDOM() LIMIT 12")
    memories = [dict(row) for row in c.fetchall()]
    conn.close()
    logging.debug(f"Returning memories: {memories}")
    return jsonify(memories)


@app.route("/sms", methods=["POST"])
def sms_reply():
    message = request.form["Body"]
    logging.debug(f"Text received: {message}")

    image_prompt_captions = get_image_prompts_captions(message, NUM_MEMORIES)
    image_prompt_captions = ast.literal_eval(image_prompt_captions)
    logging.debug(f"Prompt-caption pairs: {image_prompt_captions}")

    conn = get_db_connection()
    c = conn.cursor()

    for pair in image_prompt_captions:
        image_filename = generate_and_save_image(pair["prompt"])
        c.execute(
            "INSERT INTO memories (message, prompt, caption, image_filename) VALUES (?, ?, ?, ?)",
            (message, pair["prompt"], pair["caption"], image_filename),
        )

    conn.commit()
    conn.close()

    logging.debug("Memories stored in database")

    return "Successfully received", 200


if __name__ == "__main__":
    os.makedirs(os.path.join(static_dir, "images", "generated"), exist_ok=True)
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
