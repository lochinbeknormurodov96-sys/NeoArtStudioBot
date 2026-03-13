import os
import replicate
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

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
        await update.message.reply_text("Send description for the image")

    elif text == "Create Prompt ✍️":
        mode[user] = "prompt"
        await update.message.reply_text("Send idea for the prompt")

    else:

        if mode.get(user) == "prompt":

            result = f"{text}, cinematic lighting, ultra realistic, 8k"
            await update.message.reply_text(result)

        elif mode.get(user) == "image":

            await update.message.reply_text("Creating image... ⏳")

            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e9347b0c8e3c6a7a3b0fbbf6c7e60",
                input={"prompt": text}
            )

            image_url = output[0]

            await update.message.reply_photo(photo=image_url)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
