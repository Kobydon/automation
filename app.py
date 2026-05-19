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

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message = value["messages"][0]

            sender = message["from"]
            text = message["text"]["body"].lower()

            print("Incoming:", text)

            # =========================
            # BOT LOGIC
            # =========================
            if "hi" in text:
                send_message(sender, "How are you? 😊")

            elif "hello" in text:
                send_message(sender, "Hello there! 👋")

            else:
                send_message(sender, "I didn't understand that 🤖")

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "received"}), 200


# =========================
# TEST ROUTE
# =========================
@app.route("/")
def home():
    return "WhatsApp Bot is running 🚀"


if __name__ == "__main__":
    app.run(debug=True)