import os
import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a prompt and I will create an AI image 🎨")


def query(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    prompt = update.message.text

    await update.message.reply_text("Creating image... ⏳")

    for i in range(5):

        response = query(prompt)

        if response.headers.get("content-type") == "image/png":
            with open("image.png", "wb") as f:
                f.write(response.content)

            await update.message.reply_photo(photo=open("image.png", "rb"))
            return

        time.sleep(10)

    await update.message.reply_text("Model busy. Try again later.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, generate))

app.run_polling()
