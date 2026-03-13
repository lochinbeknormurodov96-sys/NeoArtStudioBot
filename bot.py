# NeoArtStudioBot v2
import os
import requests
import os
import requests
import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

styles = [
"cinematic lighting, ultra realistic, 8k",
"detailed digital art, fantasy style",
"dramatic atmosphere, epic scene",
"cyberpunk style, neon lights",
"anime style illustration"
]

mode = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [["Create Image 🎨", "Create Prompt ✍️"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Choose an option:",
        reply_markup=reply_markup
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.message.from_user.id

    if text == "Create Image 🎨":
        mode[user] = "image"
        await update.message.reply_text("Send a description for the image")

    elif text == "Create Prompt ✍️":
        mode[user] = "prompt"
        await update.message.reply_text("Send an idea for the prompt")

    else:

        if mode.get(user) == "prompt":

            style = random.choice(styles)
            result = f"{text}, {style}"

            await update.message.reply_text(result)

        elif mode.get(user) == "image":

            await update.message.reply_text("Creating image... ⏳")

            response = requests.post(API_URL, headers=headers, json={"inputs": text})

            if response.headers.get("content-type") == "image/png":

                with open("image.png", "wb") as f:
                    f.write(response.content)

                await update.message.reply_photo(photo=open("image.png", "rb"))

            else:

                await update.message.reply_text("Server busy. Try again later.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
