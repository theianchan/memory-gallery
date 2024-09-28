# memory-gallery

To install on new machine:
- `pip install -r requirements.txt`
- `brew install ngrok`
- Log in to `https://dashboard.ngrok.com/` for auth instructions

To run locally: 
- `source venv/bin/activate`
- `ngrok http 5001`
- Update Twilio webhook with new ngrok URL at (https://console.twilio.com/us1/develop/phone-numbers/manage/incoming/)

Note that we use 5001 since the localhost default 5000 is occupied.

When done:
- `deactivate`