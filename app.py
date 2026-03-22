import os
import json
from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "12345")
SHEET_ID = os.environ.get("SHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

def get_sheet():
    creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is running!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        messages = data["entry"][0]["changes"][0]["value"]["messages"]
        for msg in messages:
            phone = msg["from"]
            text = msg["text"]["body"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet = get_sheet()
            sheet.append_row([timestamp, phone, text])
    except Exception as e:
        print("Error:", e)
    return "OK", 200
```

Commit करा ✅

---

## `requirements.txt` पण update करा 👇
```
flask
gunicorn
gspread
google-auth
