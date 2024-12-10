from flask import Flask, request, render_template, jsonify, current_app
import threading
import os
import logging
import ast
from .config import template_dir, static_dir, NUM_MEMORIES, PHONE_NUMBER
from .database import (
    get_db_connection,
    init_db,
    init_memories_display,
    get_memories,
    get_memories_display,
)
from .images import generate_and_save_image
from .prompts import get_image_prompts_captions
from queue import Queue

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.sms_queue = Queue()
app.sms_lock = threading.Lock()
app.sms_counter = 0

memories = []


@app.route("/")
def home():
    return render_template(
        "index.html",
        phone_number=PHONE_NUMBER,
        num_memories=NUM_MEMORIES,
        memories=memories,
    )


@app.route("/view")
def view_memories():
    memories_display = get_memories_display()

    return render_template("view.html", database=memories_display)


@app.route("/view-mobile")
def view_memories_mobile():
    memories_display = get_memories_display()

    return render_template("view-mobile.html", database=memories_display)


@app.route("/memories")
def get_memories():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM memories")
    memories = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(memories)


@app.route("/working")
def get_working_status():
    return jsonify(getattr(current_app, "working", False))


@app.route("/queue_status")
def get_queue_status():
    return jsonify({"queue_size": app.sms_queue.qsize()})


@app.route("/sms", methods=["POST"])
def sms_reply():
    message = request.form["Body"]
    phone_number = request.form["From"]
    logging.debug(f"Text received from {phone_number}: {message}")

    app.sms_queue.put((message, phone_number))

    threading.Thread(target=process_sms_queue).start()

    return "Successfully received", 200


def process_sms_queue():
    with app.app_context():
        while not app.sms_queue.empty():
            message, phone_number = app.sms_queue.get()
            with app.sms_lock:
                app.sms_counter += 1

            try:
                image_prompt_captions = get_image_prompts_captions(
                    message, NUM_MEMORIES
                )
                image_prompt_captions = ast.literal_eval(image_prompt_captions)

                conn = get_db_connection()
                c = conn.cursor()

                for pair in image_prompt_captions:
                    image_filename = generate_and_save_image(pair["prompt"])
                    c.execute(
                        "INSERT INTO memories (message, prompt, caption, image_filename, phone_number) VALUES (?, ?, ?, ?, ?)",
                        (
                            message,
                            pair["prompt"],
                            pair["caption"],
                            image_filename,
                            phone_number,
                        ),
                    )

                conn.commit()
                conn.close()

                logging.debug("Memories stored in database")

            finally:
                with app.sms_lock:
                    app.sms_counter -= 1
                    if app.sms_counter == 0:
                        app.working = False

            app.sms_queue.task_done()


if __name__ == "__main__":
    os.makedirs(os.path.join(static_dir, "images", "generated"), exist_ok=True)
    init_db()
    init_memories_display()
    app.working = False
    app.run(host="0.0.0.0", port=5001, debug=True)
