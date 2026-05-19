import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# =========================
# SEND TEXT MESSAGE
# =========================
def send_message(to, text):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, json=payload, headers=headers)

    print("📤 STATUS:", response.status_code)
    print("📤 RESPONSE:", response.text)

    return response.json()


# =========================
# WEBHOOK VERIFY
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# =========================
# RECEIVE MESSAGES
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("\n🔥 INCOMING WEBHOOK:")
    print(data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        messages = value.get("messages")

        if messages:
            msg = messages[0]

            sender = msg.get("from")
            msg_type = msg.get("type")

            text = ""

            if msg_type == "text":
                text = msg.get("text", {}).get("body", "").lower()

            print("📩 MESSAGE:", text)

            if "hi" in text:
                send_message(sender, "How are you? 😊")

            elif "hello" in text:
                send_message(sender, "Hello there! 👋")

            else:
                send_message(sender, "I didn't understand 🤖")

    except Exception as e:
        print("❌ ERROR:", str(e))

    return jsonify({"status": "ok"}), 200


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "WhatsApp Bot Running 🚀"


if __name__ == "__main__":
    app.run(debug=True)