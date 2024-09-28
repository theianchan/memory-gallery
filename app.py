from flask import Flask, request, render_template_string, jsonify
# from twilio.twiml.messaging_response import MessagingResponse
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Store received messages
messages = []

@app.route('/')
def home():
    return render_template_string('''
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
                        $('#messages').empty();
                        data.forEach(function(message) {
                            $('#messages').append('<li>' + message + '</li>');
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
    ''', phone_number="+18335931560", messages=messages)

@app.route('/messages')
def get_messages():
    return jsonify(messages)

@app.route('/sms', methods=['POST'])
def sms_reply():
    message_body = request.form['Body']
    messages.append(message_body)
    
    return 'Successfully received', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)