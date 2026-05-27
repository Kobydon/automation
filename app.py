import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================================
# ENV VARIABLES
# =========================================
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# =========================================
# TEMP USER SESSION STORAGE
# =========================================
# Replace with Redis or DB in production
user_sessions = {}

# =========================================
# SEND WHATSAPP MESSAGE
# =========================================
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
        "text": {
            "body": text
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print("📤 STATUS:", response.status_code)
    print("📤 RESPONSE:", response.text)

    return response.json()


# =========================================
# SEND SAMPLE IMAGES
# =========================================
def send_image(to, image_url, caption=""):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print("🖼️ IMAGE STATUS:", response.status_code)
    print("🖼️ IMAGE RESPONSE:", response.text)

    return response.json()


# =========================================
# MAIN MENU
# =========================================
MAIN_MENU = """
Hello 👋 Welcome to Assempahfie Graphics!

Please choose an option:

1️⃣ Get a Price
2️⃣ Place an Order
3️⃣ View Samples
4️⃣ Talk to Staff

👉 Reply with a number or type your request.
"""

# =========================================
# PRICE MENU
# =========================================
PRICE_MENU = """
Great 👍 What product do you want?

1️⃣ Banner
2️⃣ Sticker / Label
3️⃣ Brochure / Book
4️⃣ T-Shirt / DTF
5️⃣ Other
"""

# =========================================
# WEBHOOK VERIFY
# =========================================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# =========================================
# SAVE ORDER
# =========================================
def save_order(data):
    """
    Replace this with:
    - Google Sheets
    - MySQL
    - PostgreSQL
    - Zapier webhook
    """

    print("\n✅ ORDER SAVED")
    print(json.dumps(data, indent=2))


# =========================================
# NOTIFY STAFF
# =========================================
def notify_staff(order_data):
    """
    Replace with:
    - WhatsApp notification
    - Email
    - Slack
    - Zapier
    """

    print("\n🚨 NEW ORDER ALERT")
    print(order_data)


# =========================================
# HANDLE PRICE FLOW
# =========================================
def handle_price_flow(sender, text, session):

    step = session.get("step")

    # =========================
    # SELECT PRODUCT
    # =========================
    if step == "awaiting_price_product":

        if text == "1" or "banner" in text:

            session["product"] = "Banner"
            session["step"] = "banner_details"

            send_message(
                sender,
                """🏳️ Banner Pricing

Please provide:
- Width
- Height
- Quantity

Example:
3ft x 6ft, 2 pieces
"""
            )

        elif text == "2" or "sticker" in text or "label" in text:

            session["product"] = "Sticker"

            session["step"] = "sticker_details"

            send_message(
                sender,
                """🏷️ Sticker / Label

Please provide:
- Type (PP Label / Paper / Transparent)
- Size
- Quantity
"""
            )

        elif text == "3" or "brochure" in text:

            send_message(
                sender,
                """📚 Brochure pricing depends on:

- Pages
- Paper Type
- Finishing

A team member will assist you shortly.
"""
            )

            notify_staff({
                "customer": sender,
                "request": "Brochure Quote"
            })

        elif text == "4" or "dtf" in text or "shirt" in text:

            session["product"] = "DTF"

            session["step"] = "dtf_details"

            send_message(
                sender,
                """👕 DTF Printing

Please provide:
- Size (A4, A3, A2)
- Quantity
"""
            )

        elif text == "5":

            session["step"] = "other_product"

            send_message(
                sender,
                "Please type the product you want."
            )

        else:
            send_message(sender, PRICE_MENU)

    # =========================
    # BANNER DETAILS
    # =========================
    elif step == "banner_details":

        session["details"] = text
        session["step"] = "banner_lamination"

        send_message(
            sender,
            """Banner prices are calculated based on size.

Would you like:
1️⃣ With lamination
2️⃣ Without lamination
"""
        )

    elif step == "banner_lamination":

        lamination = (
            "With Lamination"
            if text == "1"
            else "Without Lamination"
        )

        session["lamination"] = lamination

        send_message(
            sender,
            f"""✅ Banner Quote Request Received

Product: Banner
Details: {session.get("details")}
Finish: {lamination}

A team member will send your quote shortly.
"""
        )

        notify_staff(session)

    # =========================
    # STICKER DETAILS
    # =========================
    elif step == "sticker_details":

        session["details"] = text
        session["step"] = "sticker_finish"

        send_message(
            sender,
            """Do you want:

1️⃣ Print only
2️⃣ Print & Cut
"""
        )

    elif step == "sticker_finish":

        finish = (
            "Print Only"
            if text == "1"
            else "Print & Cut"
        )

        session["finish"] = finish

        send_message(
            sender,
            f"""✅ Sticker Quote Request Received

Details: {session.get("details")}
Finish: {finish}

Our team will contact you shortly.
"""
        )

        notify_staff(session)

    # =========================
    # DTF DETAILS
    # =========================
    elif step == "dtf_details":

        session["details"] = text

        send_message(
            sender,
            f"""✅ DTF Quote Request Received

Details:
{text}

A team member will contact you shortly.
"""
        )

        notify_staff(session)

    # =========================
    # OTHER PRODUCT
    # =========================
    elif step == "other_product":

        send_message(
            sender,
            f"""Got it 👍 You want:

{text}

Please provide:
- Size
- Quantity
"""
        )

        session["product"] = text
        session["step"] = "other_details"

    elif step == "other_details":

        session["details"] = text

        send_message(
            sender,
            """✅ Quote Request Received

A team member will assist you shortly.
"""
        )

        notify_staff(session)


# =========================================
# HANDLE ORDER FLOW
# =========================================
def handle_order_flow(sender, text, session):

    step = session.get("step")

    if step == "awaiting_order_details":

        session["order_details"] = text

        save_order({
            "phone": sender,
            "details": text,
            "status": "Pending"
        })

        notify_staff({
            "phone": sender,
            "details": text
        })

        send_message(
            sender,
            """✅ Thank you!

Your order is being processed.

A team member will confirm shortly.
"""
        )

        session["step"] = "completed"


# =========================================
# HANDLE SAMPLE FLOW
# =========================================
def handle_samples(sender, text):

    if text == "1":
        send_image(
            sender,
            "https://yourdomain.com/banner.jpg",
            "Banner Samples"
        )

    elif text == "2":
        send_image(
            sender,
            "https://yourdomain.com/sticker.jpg",
            "Sticker Samples"
        )

    elif text == "3":
        send_image(
            sender,
            "https://yourdomain.com/brochure.jpg",
            "Brochure Samples"
        )

    elif text == "4":
        send_image(
            sender,
            "https://yourdomain.com/tshirt.jpg",
            "T-Shirt Samples"
        )

    else:
        send_message(
            sender,
            """Sure 👍 Here are some of our samples:

1️⃣ Banners
2️⃣ Stickers
3️⃣ Brochures
4️⃣ T-Shirts
"""
        )


# =========================================
# MAIN WEBHOOK
# =========================================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("\n🔥 INCOMING WEBHOOK")
    print(json.dumps(data, indent=2))

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
                text = msg.get("text", {}).get("body", "").strip().lower()

            print("📩 MESSAGE:", text)

            # =========================================
            # CREATE SESSION
            # =========================================
            if sender not in user_sessions:
                user_sessions[sender] = {}

            session = user_sessions[sender]

            # =========================================
            # GREETINGS
            # =========================================
            greetings = [
                "hi",
                "hello",
                "hey",
                "good morning",
                "good afternoon",
                "good evening"
            ]

            if text in greetings:

                session["step"] = "main_menu"

                send_message(sender, MAIN_MENU)

            # =========================================
            # MAIN MENU
            # =========================================
            elif text == "1":

                session["flow"] = "price"
                session["step"] = "awaiting_price_product"

                send_message(sender, PRICE_MENU)

            elif text == "2":

                session["flow"] = "order"
                session["step"] = "awaiting_order_details"

                send_message(
                    sender,
                    """Great 👍 Let’s place your order.

Please provide:
- Product
- Size
- Quantity
- Any design file (optional)
"""
                )

            elif text == "3":

                session["flow"] = "samples"

                send_message(
                    sender,
                    """Sure 👍 Here are some of our samples:

1️⃣ Banners
2️⃣ Stickers
3️⃣ Brochures
4️⃣ T-Shirts
"""
                )

            elif text == "4":

                send_message(
                    sender,
                    """👨‍💼 Connecting you to a team member now...
"""
                )

                notify_staff({
                    "customer": sender,
                    "request": "Talk to Staff"
                })

            # =========================================
            # DIRECT PRODUCT DETECTION
            # =========================================
            elif any(
                word in text
                for word in [
                    "banner",
                    "sticker",
                    "label",
                    "dtf",
                    "shirt",
                    "brochure"
                ]
            ):

                session["flow"] = "price"
                session["step"] = "awaiting_price_product"

                handle_price_flow(sender, text, session)

            # =========================================
            # CONTINUE PRICE FLOW
            # =========================================
            elif session.get("flow") == "price":

                handle_price_flow(sender, text, session)

            # =========================================
            # CONTINUE ORDER FLOW
            # =========================================
            elif session.get("flow") == "order":

                handle_order_flow(sender, text, session)

            # =========================================
            # SAMPLE FLOW
            # =========================================
            elif session.get("flow") == "samples":

                handle_samples(sender, text)

            # =========================================
            # UNKNOWN MESSAGE
            # =========================================
            else:

                send_message(
                    sender,
                    """Sorry, I didn’t fully understand.

Please choose:
1️⃣ Get a Price
2️⃣ Place an Order
3️⃣ View Samples
4️⃣ Talk to Staff
"""
                )

    except Exception as e:

        print("❌ ERROR:", str(e))

    return jsonify({
        "status": "ok"
    }), 200


# =========================================
# HOME
# =========================================
@app.route("/")
def home():
    return "🚀 Assempahfie Graphics WhatsApp Bot Running"


# =========================================
# RUN APP
# =========================================
if __name__ == "__main__":
    app.run(debug=True)