import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # for webhook verification


# =========================
# SEND MESSAGE FUNCTION
# =========================
def send_message(to, text):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    return requests.post(url, json=data, headers=headers).json()


# =========================
# WEBHOOK VERIFY (META CHECK)
# =========================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# =========================
# RECEIVE MESSAGES (MAIN BOT LOGIC)
# =========================
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    print("\n🔥🔥🔥 WEBHOOK HIT CONFIRMED 🔥🔥🔥")
    print(data)

    return "OK", 200


# =========================
# TEST ROUTE
# =========================
@app.route("/")
def home():
    return "WhatsApp Bot is running 🚀"


if __name__ == "__main__":
    app.run(debug=True)