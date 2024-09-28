from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Store received messages
messages = []

@app.route('/')
def home():
    return render_template_string('''
        <h1>Text your message to {{ phone_number }}</h1>
        <h2>Received Messages:</h2>
        <ul>
        {% for message in messages %}
            <li>{{ message }}</li>
        {% endfor %}
        </ul>
    ''', phone_number="+18335931560", messages=messages)

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Log the incoming request
    app.logger.debug(f"Received SMS webhook. Headers: {request.headers}")
    app.logger.debug(f"Form data: {request.form}")
    app.logger.debug(f"Full URL: {request.url}")

    # Rest of your code here
    message_body = request.form['Body']
    messages.append(message_body)
    
    # resp = MessagingResponse()
    # resp.message("Thank you for your message!")
    
    # return str(resp)
    return 'Successfully received', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)