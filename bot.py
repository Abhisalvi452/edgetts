from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

# Replace with your webhook URL (provided by Render or Codeberg)
WEBHOOK_URL = "https://your-render-or-codeberg-url.com/webhook"

# Set webhook
def set_webhook():
    url = TELEGRAM_API_URL + "setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    return response.json()

# Handle incoming messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    # Echo the message back
    send_message(chat_id, f"You said: {text}")
    return "OK"

# Send a message to the user
def send_message(chat_id, text):
    url = TELEGRAM_API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

# Start the bot
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=8000)
