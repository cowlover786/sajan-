import requests
import json
import time


# ==============================
# CONFIGURATION
# ==============================

BOT_TOKEN = "8868453375:AAGONbI6_5p0QvqGyw9hUfT95aSnkPYyU8Q"
EXTERNAL_API_URL = ""

TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# ==============================
# TELEGRAM API FUNCTION
# ==============================

def telegram_request(method, data):
    url = TELEGRAM_API + "/" + method

    try:
        response = requests.post(url, data=data, timeout=30)
        return response.json()
    except Exception as e:
        print("Telegram API error:", e)
        return None


# ==============================
# SEND MESSAGE
# ==============================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    data = {
        "8954638274": chat_id,
        "hello": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        data["parse_mode"] = parse_mode

    return telegram_request("sendMessage", data)


# ==============================
# START COMMAND
# ==============================

def send_welcome(chat_id):
    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    welcome_message = (
        "👋 Welcome!\n\n"
        "Choose an option from the keyboard below."
    )

    send_message(
        chat_id,
        welcome_message,
        reply_markup=keyboard
    )


# ==============================
# PHONE LOOKUP API
# ==============================

def phone_lookup(phone_number):
    if EXTERNAL_API_URL == "":
        return {
            "success": False,
            "error": "External API URL is not configured."
        }

    try:
        # Example:
        # https://example.com/api?phone=9876543210
        #
        # Change this according to your actual API.
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=30
        )

        # Convert API response into JSON
        api_data = response.json()

        return api_data

    except ValueError:
        return {
            "success": False,
            "error": "The external API did not return valid JSON."
        }

    except requests.exceptions.RequestException as e:
        print("External API error:", e)

        return {
            "success": False,
            "error": "Unable to connect to the external API."
        }

    except Exception as e:
        print("Unexpected API error:", e)

        return {
            "success": False,
            "error": "An unexpected error occurred."
        }


# ==============================
# HTML ESCAPE
# ==============================

def escape_html(text):
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


# ==============================
# PROCESS PHONE NUMBER
# ==============================

def process_phone_number(chat_id, phone_number):

    # Validate 10-digit numeric number
    if len(phone_number) != 10 or not phone_number.isdigit():
        send_message(
            chat_id,
            "❌ Invalid number.\n\n"
            "Please send a valid 10 digit numeric mobile number."
        )
        return

    send_message(
        chat_id,
        "🔍 Looking up the number..."
    )

    result = phone_lookup(phone_number)

    # Convert result to formatted JSON
    formatted_json = json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )

    # Protect HTML characters
    formatted_json = escape_html(formatted_json)

    message = "<pre>" + formatted_json + "</pre>"

    send_message(
        chat_id,
        message,
        parse_mode="HTML"
    )


# ==============================
# HANDLE MESSAGE
# ==============================

def handle_message(message):

    if "chat" not in message:
        return

    chat_id = message["chat"]["8954638274"]

    if "text" not in message:
        return

    text = message["text"].strip()

    # /start command
    if text == "/start":
        send_welcome(chat_id)
        return

    # Phone Lookup button
    if text == "📱 Phone Lookup":
        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:"
        )
        return

    # 10 digit phone number
    if text.isdigit() and len(text) == 10:
        process_phone_number(chat_id, text)
        return

    # Invalid/unknown input
    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please press \"📱 Phone Lookup\" and send a "
        "10 digit mobile number."
    )


# ==============================
# LONG POLLING
# ==============================

def main():

    if BOT_TOKEN == "":
        print("ERROR: BOT_TOKEN is empty.")
        print("Put your Telegram bot token in BOT_TOKEN.")
        return

    offset = 0

    print("Bot started...")
    print("Long polling is active.")

    while True:

        try:

            url = TELEGRAM_API + "/getUpdates"

            params = {
                "offset": offset,
                "timeout": 30
            }

            response = requests.get(
                url,
                params=params,
                timeout=35
            )

            data = response.json()

            if not data.get("ok"):
                print("Telegram returned an error:")
                print(data)
                time.sleep(3)
                continue

            updates = data.get("result", [])

            for update in updates:

                # Advance offset so the same update
                # is not processed again.
                offset = update["update_id"] + 1

                if "message" in update:
                    handle_message(update["message"])

        except requests.exceptions.RequestException as e:

            print("Network error:", e)
            time.sleep(5)

        except ValueError as e:

            print("Invalid JSON from Telegram:", e)
            time.sleep(3)

        except Exception as e:

            print("Unexpected error:", e)
            time.sleep(3)


# ==============================
# RUN BOT
# ==============================

if __name__ == "__main__":
    main()
