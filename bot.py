import os
import requests
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

user_mode = {}

def query(prompt):
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "options": {"wait_for_model": True}
        }
    )
    return response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [["Create Image 🎨"], ["Create Prompt ✏️"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Choose a function:",
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Create Image 🎨":
        user_mode[user_id] = "image"
        await update.message.reply_text("Send me what image you want to generate.")
        return

    if text == "Create Prompt ✏️":
        user_mode[user_id] = "prompt"
        await update.message.reply_text("Send me your idea and I will improve the prompt.")
        return

    if user_id not in user_mode:
        await update.message.reply_text("Press /start first.")
        return

    mode = user_mode[user_id]

    if mode == "prompt":

        prompt = f"{text}, cinematic lighting, ultra detailed, 8k, masterpiece"

        await update.message.reply_text(prompt)
        return

    if mode == "image":

        prompt = text

        await update.message.reply_text("Creating image... ⏳")

        for i in range(10):

            response = query(prompt)

            if response.headers.get("content-type") == "image/png":

                with open("image.png", "wb") as f:
                    f.write(response.content)

                await update.message.reply_photo(photo=open("image.png", "rb"))
                return

            time.sleep(8)

        await update.message.reply_text("Server busy. Try again later.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, message_handler))

app.run_polling()
