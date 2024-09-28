from flask import Flask, request, render_template_string, jsonify
import anthropic
import os
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

messages = []


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
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SMS Messages</title>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
                function fetchMessages() {
                    $.getJSON('/messages', function(data) {
                        console.log('messages:', data);
                        $('#messages').empty();
                        data.forEach(function(item) {
                            $('#messages').append('<li>Message: ' + item.message + '<br>Claude: ' + item.claude_response + '</li>');
                        });
                    });
                }

                $(document).ready(function() {
                    fetchMessages();
                    setInterval(fetchMessages, 5000);  // Fetch messages every 5 seconds
                });
            </script>
        </head>
        <body>
            <h1>Text your message to {{ phone_number }}</h1>
            <h2>Received Messages:</h2>
            <ul id="messages">
            </ul>
        </body>
        </html>
    """,
        phone_number="+18335931560",
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

    messages.append({"message": message_body, "claude_response": claude_response})
    logging.debug(f"Messages after append: {messages}")

    return "Successfully received", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
