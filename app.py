import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from edge_tts import Communicate, list_voices
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

# Replace with your bot token (use environment variable)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global variables to store user preferences
user_preferences = {}

# Initialize the bot application
application = Application.builder().token(BOT_TOKEN).build()

# Initialize the application (add this line)
async def initialize_app():
    await application.initialize()

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎤 Select Voice", callback_data="select_voice")],
        [InlineKeyboardButton("📏 Set Rate", callback_data="set_rate")],
        [InlineKeyboardButton("🎵 Set Pitch", callback_data="set_pitch")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Edge-TTS Bot! 🎤\n\n"
        "Use the buttons below to customize your TTS settings:",
        reply_markup=reply_markup,
    )

# Callback: Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "select_voice":
        await select_voice_menu(query)
    elif data.startswith("voice_"):
        voice = data.replace("voice_", "")
        user_preferences[user_id] = user_preferences.get(user_id, {})
        user_preferences[user_id]["voice"] = voice
        await query.edit_message_text(f"✅ Voice selected: {voice}")
    elif data == "set_rate":
        await set_rate_menu(query)
    elif data.startswith("rate_"):
        rate = data.replace("rate_", "")
        user_preferences[user_id] = user_preferences.get(user_id, {})
        user_preferences[user_id]["rate"] = rate
        await query.edit_message_text(f"✅ Rate set to: {rate}")
    elif data == "set_pitch":
        await set_pitch_menu(query)
    elif data.startswith("pitch_"):
        pitch = data.replace("pitch_", "")
        user_preferences[user_id] = user_preferences.get(user_id, {})
        user_preferences[user_id]["pitch"] = pitch
        await query.edit_message_text(f"✅ Pitch set to: {pitch}")
    elif data == "back_to_main":
        await start(query, context)

# Menu: Select Voice
async def select_voice_menu(query):
    voices = await list_voices()
    voice_groups = {}

    # Group voices by language and gender
    for voice in voices:
        language = voice["ShortName"].split("-")[0]
        gender = voice["Gender"]
        key = f"{language} ({gender})"
        if key not in voice_groups:
            voice_groups[key] = []
        voice_groups[key].append(voice["ShortName"])

    # Create buttons for each voice
    keyboard = []
    for group, voices_in_group in voice_groups.items():
        for voice in voices_in_group:
            keyboard.append([InlineKeyboardButton(voice, callback_data=f"voice_{voice}")])

    # Add a back button
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a voice:", reply_markup=reply_markup)

# Menu: Set Rate
async def set_rate_menu(query):
    keyboard = [
        [InlineKeyboardButton("+20%", callback_data="rate_+20%")],
        [InlineKeyboardButton("+10%", callback_data="rate_+10%")],
        [InlineKeyboardButton("Default (0%)", callback_data="rate_+0%")],
        [InlineKeyboardButton("-10%", callback_data="rate_-10%")],
        [InlineKeyboardButton("-20%", callback_data="rate_-20%")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a speech rate:", reply_markup=reply_markup)

# Menu: Set Pitch
async def set_pitch_menu(query):
    keyboard = [
        [InlineKeyboardButton("+20Hz", callback_data="pitch_+20Hz")],
        [InlineKeyboardButton("+10Hz", callback_data="pitch_+10Hz")],
        [InlineKeyboardButton("Default (0Hz)", callback_data="pitch_+0Hz")],
        [InlineKeyboardButton("-10Hz", callback_data="pitch_-10Hz")],
        [InlineKeyboardButton("-20Hz", callback_data="pitch_-20Hz")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a pitch:", reply_markup=reply_markup)

# Handle text messages - Convert text to speech
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if not text:
        await update.message.reply_text("Please send some text to convert to speech.")
        return

    # Get user preferences
    voice = user_preferences.get(user_id, {}).get("voice", "en-US-AriaNeural")
    rate = user_preferences.get(user_id, {}).get("rate", "+0%")
    pitch = user_preferences.get(user_id, {}).get("pitch", "+0Hz")

    # Generate speech
    output_file = f"{user_id}_output.mp3"
    communicate = Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)

    # Send the audio file
    with open(output_file, "rb") as audio_file:
        await update.message.reply_audio(audio_file)

    # Clean up the file
    os.remove(output_file)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Initialize the application before starting the Flask app
if __name__ == "__main__":
    asyncio.run(initialize_app())  # Initialize the application
    port = int(os.getenv("PORT", 10000))  # Use Render's PORT or default to 10000
    app.run(host="0.0.0.0", port=port)
