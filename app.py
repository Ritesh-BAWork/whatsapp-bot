import os
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "12345")

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
    print("Incoming:", data)
    return "OK", 200
```

**1.6** → खाली **"Commit changes"** button click करा ✅

---

## STEP 2 — Render Redeploy करा

**2.1** → [dashboard.render.com](https://dashboard.render.com) वर जा

**2.2** → `whatsapp-webhook` service वर click करा

**2.3** → उजव्या बाजूला **"Manual Deploy"** button click करा

**2.4** → **"Deploy latest commit"** select करा

**2.5** → Logs मध्ये हे दिसेपर्यंत wait करा:
```
==> Your service is live 🎉
```

---

## STEP 3 — Test करा

Browser मध्ये हे 3 URLs टाका एक एक करून:

**Test 1:**
```
https://whatsapp-webhook-f8nl.onrender.com/
```
✅ दिसलं पाहिजे: `WhatsApp Bot is running!`

**Test 2:**
```
https://whatsapp-webhook-f8nl.onrender.com/webhook
```
✅ दिसलं पाहिजे: `Verification failed`

**Test 3:**
```
https://whatsapp-webhook-f8nl.onrender.com/webhook?hub.mode=subscribe&hub.verify_token=12345&hub.challenge=999
```
✅ दिसलं पाहिजे: `999`

---

## STEP 4 — Cron-job.org Setup करा

**4.1** → [cron-job.org](https://cron-job.org) वर जा

**4.2** → **"Sign Up"** करा (free, no credit card)

**4.3** → Login केल्यावर **"CREATE CRONJOB"** click करा

**4.4** → हे fill करा:

| Field | Value |
|---|---|
| Title | Keep Render Alive |
| URL | `https://whatsapp-webhook-f8nl.onrender.com/` |
| Schedule | Every 5 minutes |

**4.5** → **"CREATE"** button click करा ✅

---

## STEP 5 — Meta Webhook Verify करा

**5.1** → [developers.facebook.com](https://developers.facebook.com) वर जा

**5.2** → तुमचा App select करा

**5.3** → WhatsApp → Configuration वर जा

**5.4** → Webhook URL टाका:
```
https://whatsapp-webhook-f8nl.onrender.com/webhook
```

**5.5** → Verify Token टाका:
```
12345
