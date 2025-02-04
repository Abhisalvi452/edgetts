import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get environment variables
TOKEN = os.environ.get('TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# Create Telegram bot objects
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Define command handlers
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm a serverless bot deployed on Render!"
    )

dispatcher.add_handler(CommandHandler("start", start))

@app.post('/webhook')
def webhook():
    """Handle incoming Telegram updates"""
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return '', 200

@app.route('/')
def health_check():
    return "Bot is running!", 200

def set_webhook():
    """Set Telegram webhook"""
    webhook_url = f"{WEBHOOK_URL}/webhook"
    logger.info(f"Setting webhook: {webhook_url}")
    bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    set_webhook()
    app.run(host='0.0.0.0', port=PORT)
