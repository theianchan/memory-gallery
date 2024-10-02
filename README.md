# memory-gallery

To install on new machine:
- `pip install -r requirements.txt`
- `brew install ngrok`
- Log in to `https://dashboard.ngrok.com/` for auth instructions
- Create a `.env` file with 
```
ANTHROPIC_API_KEY=$KEY
STABILITY_API_KEY=$KEY
PHONE_NUMBER=$PHONE
```

To run locally: 
- `source venv/bin/activate`
- `NUM_MEMORIES=2 python app.py` (or whatever number of memories you want)
- `ngrok http 5001`
- Update Twilio webhook with new ngrok URL at (https://console.twilio.com/us1/develop/phone-numbers/manage/incoming/)

Note that we use 5001 since the localhost default 5000 is occupied.

`pip freeze > requirements.txt` when new libraries are installed.

To view database:
- `sqlite3 memories.db`
- `select * from memories;`

Remaining TODO:
- Database storage (implemented)
- Display order
- Enhanced error handling (not extremely worried about this)
- Input validation (or this)
- Async processing (seems to handle this pretty well already)
- Production-ready logging (added a bunch more logs)