import os
import gdown
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("📥 Send me a Google Drive link!")

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def extract_file_id(url):
    if "id=" in url:
        return url.split("id=")[1].split("&")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Google Drive link")

def get_filename_from_drive(file_id):
    url = f"https://drive.google.com/file/d/{file_id}/view"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    name_tag = soup.find("meta", {"property": "og:title"})
    if name_tag:
        return name_tag["content"]
    return "downloaded_file"

def handle_link(update: Update, context: CallbackContext):
    url = update.message.text
    if "drive.google.com" not in url:
        update.message.reply_text("❌ Invalid Google Drive link.")
        return

    status = update.message.reply_text("🔗 Starting...")

    try:
        file_id = extract_file_id(url)
        filename = get_filename_from_drive(file_id)
        output = filename

        # Download with gdown
        gdown.download(url, output, quiet=False)

        file_size = os.path.getsize(output) / (1024 * 1024)
        if file_size <= 1990:
            status.edit_text("📤 Uploading to Telegram...")
            with open(output, 'rb') as f:
                update.message.reply_document(f, filename=filename)
            status.edit_text("✅ Done!")
        else:
            status.edit_text(f"⚠️ File too big for Telegram: {file_size:.2f}MB")

        os.remove(output)

    except Exception as e:
        status.edit_text(f"❌ Error: {str(e)}")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
