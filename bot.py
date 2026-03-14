import os
import requests
import time
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

IMAGE_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
UPSCALE_API = "https://api-inference.huggingface.co/models/caidas/swin2SR-realworld-sr-x4-64-bsrgan-psnr"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

user_mode = {}
user_last_prompt = {}

# --- Helpers ---
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

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Create 4 Images 🎨"], ["Create Prompt ✏️"], ["HD Image 🔎"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose a function:", reply_markup=reply_markup)

# --- Main message handler ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Create 4 Images 🎨":
        user_mode[user_id] = "image"
        await update.message.reply_text("Send a description for 4 AI images.")
        return

    if text == "Create Prompt ✏️":
        user_mode[user_id] = "prompt"
        await update.message.reply_text("Send your idea, I will enhance the prompt.")
        return

    if text == "HD Image 🔎":
        user_mode[user_id] = "hd"
        await update.message.reply_text("Send an image to upscale to HD / trend style.")
        return

    if user_id not in user_mode:
        await update.message.reply_text("Press /start first.")
        return

    mode = user_mode[user_id]

    # --- Prompt generator ---
    if mode == "prompt":
        prompt = f"{text}, cinematic lighting, ultra detailed, 8k, masterpiece, trend style"
        await update.message.reply_text(prompt)
        return

    # --- Image generation ---
    if mode == "image":
        user_last_prompt[user_id] = text
        await update.message.reply_text("Creating 4 HD images... ⏳")
        for i in range(1, 5):
            response = query_image(f"{text}, ultra realistic, 8k, highly detailed, cinematic lighting, trend style, seed {i}")
            if response.headers.get("content-type") == "image/png":
                filename = f"image_{i}_{user_id}.png"
                with open(filename, "wb") as f:
                    f.write(response.content)
                # Add inline button for HD/upscale
                buttons = [[InlineKeyboardButton("Make HD 🔎", callback_data=filename)]]
                markup = InlineKeyboardMarkup(buttons)
                await update.message.reply_photo(photo=open(filename, "rb"), reply_markup=markup)
            else:
                await update.message.reply_text(f"Image {i} generation failed, server busy. Try again later.")

# --- Upscale handler ---
async def upscale_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    filename = query.data

    with open(filename, "rb") as f:
        image_bytes = f.read()

    await query.message.reply_text("Upscaling image to HD / trend style... ⏳")
    response = query_upscale(image_bytes)

    if response.headers.get("content-type") == "image/png":
        hd_filename = f"HD_{filename}"
        with open(hd_filename, "wb") as f:
            f.write(response.content)
        await query.message.reply_photo(photo=open(hd_filename, "rb"))
    else:
        await query.message.reply_text("Upscale failed. Try another image.")

# --- HD image via photo ---
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
app.add_handler(CallbackQueryHandler(upscale_callback))

app.run_polling()
