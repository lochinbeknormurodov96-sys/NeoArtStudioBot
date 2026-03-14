import os
import requests
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")         # Telegram bot token
HF_TOKEN = os.getenv("HF_TOKEN")   # Hugging Face token

# AI Model API
IMAGE_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
UPSCALE_API = "https://api-inference.huggingface.co/models/caidas/swin2SR-realworld-sr-x4-64-bsrgan-psnr"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# User mode tracking
user_mode = {}

# --- Helper functions ---
def query_image(prompt):
    response = requests.post(
        IMAGE_API,
        headers=HEADERS,
        json={"inputs": prompt, "options": {"wait_for_model": True}}
    )
    return response

def query_upscale(image_bytes):
    response = requests.post(
        UPSCALE_API,
        headers=HEADERS,
        data=image_bytes
    )
    return response

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Create Image 🎨"], ["Create Prompt ✏️"], ["HD Image 🔎"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose a function:", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Create Image 🎨":
        user_mode[user_id] = "image"
        await update.message.reply_text("Send me the description of the image you want to generate.")
        return

    if text == "Create Prompt ✏️":
        user_mode[user_id] = "prompt"
        await update.message.reply_text("Send me your idea, I will enhance the prompt.")
        return

    if text == "HD Image 🔎":
        user_mode[user_id] = "hd"
        await update.message.reply_text("Send me an image to make it HD / trend style.")
        return

    if user_id not in user_mode:
        await update.message.reply_text("Press /start first.")
        return

    mode = user_mode[user_id]

    # --- Prompt mode ---
    if mode == "prompt":
        prompt = f"{text}, cinematic lighting, ultra detailed, 8k, masterpiece, trend style"
        await update.message.reply_text(prompt)
        return

    # --- Image generation mode ---
    if mode == "image":
        prompt = f"{text}, ultra realistic, 8k, highly detailed, cinematic lighting, trend style"
        await update.message.reply_text("Creating HD image... ⏳")

        for _ in range(10):
            response = query_image(prompt)
            if response.headers.get("content-type") == "image/png":
                with open("image.png", "wb") as f:
                    f.write(response.content)
                await update.message.reply_photo(photo=open("image.png", "rb"))
                return
            time.sleep(8)

        await update.message.reply_text("Server busy. Try again later.")

# --- HD / Upscale handler ---
async def upscale_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_mode.get(user_id) != "hd":
        return

    if not update.message.photo:
        await update.message.reply_text("Send a photo for HD enhancement.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = requests.get(file.file_path).content

    await update.message.reply_text("Enhancing image to HD / trend style... ⏳")

    response = query_upscale(image_bytes)
    if response.headers.get("content-type") == "image/png":
        with open("hd.png", "wb") as f:
            f.write(response.content)
        await update.message.reply_photo(photo=open("hd.png", "rb"))
    else:
        await update.message.reply_text("Upscale failed. Try another image.")

# --- Main ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.PHOTO, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, upscale_image))

app.run_polling()
