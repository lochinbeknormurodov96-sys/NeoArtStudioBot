import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random

TOKEN = os.getenv("TOKEN")

prompts = [
"cinematic lighting, ultra realistic, 8k",
"detailed digital art, fantasy style",
"dramatic atmosphere, epic scene",
"highly detailed concept art",
"cyberpunk style, neon lights",
"anime style illustration"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any idea and I will generate an AI image prompt 🎨")

async def generate_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea = update.message.text
    style = random.choice(prompts)
    result = f"{idea}, {style}"
    await update.message.reply_text(result)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, generate_prompt))
app.run_polling()
