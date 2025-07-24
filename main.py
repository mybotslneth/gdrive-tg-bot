import os
import gdown
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Send me a Google Drive link to download and upload to Telegram!")

def handle_link(update: Update, context: CallbackContext):
    url = update.message.text
    if "drive.google.com" not in url:
        update.message.reply_text("❌ Invalid Google Drive link.")
        return

    update.message.reply_text("📥 Downloading file... Please wait ⏳")

    try:
        output = 'downloaded_file'
        gdown.download(url, output, quiet=False)
        file_size = os.path.getsize(output) / (1024 * 1024)

        if file_size <= 1990:
            with open(output, 'rb') as f:
                update.message.reply_document(f)
            update.message.reply_text("✅ File uploaded successfully!")
        else:
            update.message.reply_text(f"❌ File too big for Telegram upload ({file_size:.2f}MB).")
        os.remove(output)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
