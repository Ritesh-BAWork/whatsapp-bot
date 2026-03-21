from flask import Flask, request, jsonify
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "12345")
SHEET_ID = os.environ.get("SHEET_ID")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gsheet():
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet("WhatsApp Messages")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="WhatsApp Messages", rows=1000, cols=10)
        ws.append_row([
            "Received At",
            "Client Name",
            "WhatsApp Number",
            "Message Type",
            "Message Text",
            "Item",
            "Qty",
            "Note",
            "Message ID",
            "Raw JSON"
        ])
    return ws

def extract_message_text(message, msg_type):
    if msg_type == "text":
        return message.get("text", {}).get("body", "")
    if msg_type == "image":
        return message.get("image", {}).get("caption", "[Image]")
    if msg_type == "video":
        return message.get("video", {}).get("caption", "[Video]")
    if msg_type == "audio":
        return "[Audio Message]"
    if msg_type == "document":
        name = message.get("document", {}).get("filename", "document")
        return f"[Document: {name}]"
    if msg_type == "button":
        return message.get("button", {}).get("text", "[Button]")
    return f"[{msg_type}]"

@app.get("/")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge or "", 200
    return "Verification failed", 403

@app.post("/")
def webhook():
    try:
        payload = request.get_json(force=True, silent=True) or {}

        entry = payload.get("entry", [])
        if not entry:
            return jsonify({"status": "ok", "note": "No entry"}), 200

        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "ok", "note": "No changes"}), 200

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        if not messages:
            return jsonify({"status": "ok", "note": "No messages"}), 200

        ws = get_gsheet()

        existing_ids = set()
        try:
            col_values = ws.col_values(9)
            existing_ids = set(col_values[1:]) if len(col_values) > 1 else set()
        except Exception:
            existing_ids = set()

        rows = []

        for msg in messages:
            msg_id = msg.get("id", "")
            if msg_id and msg_id in existing_ids:
                continue

            wa_id = msg.get("from", "")
            msg_type = msg.get("type", "unknown")
            msg_text = extract_message_text(msg, msg_type)

            client_name = "Unknown"
            for c in contacts:
                if c.get("wa_id") == wa_id:
                    client_name = c.get("profile", {}).get("name", "Unknown")
                    break
            if client_name == "Unknown" and contacts:
                client_name = contacts[0].get("profile", {}).get("name", "Unknown")

            rows.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_name,
                wa_id,
                msg_type,
                msg_text,
                "",
                "",
                "",
                msg_id,
                json.dumps(msg, ensure_ascii=False)
            ])

        if rows:
            ws.append_rows(rows, value_input_option="RAW")

        return jsonify({"status": "ok", "stored": len(rows)}), 200

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
