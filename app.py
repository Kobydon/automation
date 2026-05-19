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
        "text": {"body": text}
    }

    response = requests.post(url, json=data, headers=headers)

    print("📤 SEND STATUS:", response.status_code)
    print("📤 SEND RESPONSE:", response.json())

    return response.json()

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

    # 🔥 DEBUG: always show incoming payload
    print("\n🔥 WEBHOOK RECEIVED:")
    print(data)

    try:
        if not data:
            return "OK", 200

        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        messages = value.get("messages")

        if messages:
            message = messages[0]

            sender = message.get("from")

            msg_type = message.get("type")
            text = ""

            # ✅ safe text extraction
            if msg_type == "text":
                text = message.get("text", {}).get("body", "").lower()

            print("📩 Incoming text:", text)

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
        print("❌ ERROR:", str(e))

    return jsonify({"status": "received"}), 200


# =========================
# TEST ROUTE
# =========================
@app.route("/")
def home():
    return "WhatsApp Bot is running 🚀"


if __name__ == "__main__":
    app.run(debug=True)