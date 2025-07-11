import logging
from telegram import Update, File
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
TELEGRAM_BOT_TOKEN = "8165719767:AAE6bx5EtVqL4B3jYWZdYl6C-8lbnAHkJSE"
DOWNLOAD_DIR = "downloads"

# Create the downloads directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Send me any PDF or image, and I'll try to organize it for you.",
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming documents (PDFs)."""
    document = update.message.document
    chat_id = update.effective_chat.id

    if document:
        if document.mime_type == 'application/pdf':
            file_name = document.file_name
            await update.message.reply_text(f"Received PDF: {file_name}. Processing...")

            # Get file information from Telegram
            telegram_file: File = await context.bot.get_file(document.file_id)

            local_file_path = os.path.join(DOWNLOAD_DIR, file_name)

            try:
                # Download the file
                await telegram_file.download_to_drive(local_file_path)
                await update.message.reply_text(f"Saved PDF to: {local_file_path}")
                logger.info(f"Downloaded PDF: {file_name} to {local_file_path}")

                # --- HERE YOU WILL INTEGRATE YOUR OCR AND AI LOGIC ---
                # For now, let's just confirm receipt.
                # In later steps, you'll call functions like:
                # extracted_text = perform_ocr(local_file_path)


            except Exception as e:
                logger.error(f"Error downloading PDF {file_name}: {e}")
                await update.message.reply_text(f"Sorry, I couldn't download your PDF. Error: {e}")

        else:
            await update.message.reply_text("I can only process PDF documents for now. Please send a PDF.")
            logger.info(f"Received non-PDF document: {document.mime_type}")
    else:
        await update.message.reply_text("I received a message, but it doesn't seem to be a document I can process.")
        logger.info("Received a message without a document.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming photos (images)."""

    photo = update.message.photo[-1]
    chat_id = update.effective_chat.id

    await update.message.reply_text("Received an image. Processing...")

    # Get file information from
    telegram_file: File = await context.bot.get_file(photo.file_id)

    file_extension = "jpg"  # Default to jpg,
    local_file_path = os.path.join(DOWNLOAD_DIR, f"{photo.file_id}.{file_extension}")

    try:
        # Download the file
        await telegram_file.download_to_drive(local_file_path)
        await update.message.reply_text(f"Saved image to: {local_file_path}")
        logger.info(f"Downloaded image: {local_file_path}")


    except Exception as e:
        logger.error(f"Error downloading image {photo.file_id}: {e}")
        await update.message.reply_text(f"Sorry, I couldn't download your image. Error: {e}")


async def echo_non_document_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
"
    if update.message.text:
        await update.message.reply_text("I'm designed to process PDFs and images. Please send one!")
    else:
        await update.message.reply_text("I received something, but it's not a PDF, image, or text I understand.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # Add handlers for different types of messages
    # MessageHandler for documents (PDFs)
    application.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_document))
    # MessageHandler for photos (images)
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    # MessageHandler for any other text/media not handled above
    application.add_handler(
        MessageHandler(filters.TEXT | filters.ATTACHMENT & ~filters.COMMAND, echo_non_document_messages))

    logger.info("Bot is starting... Listening for updates via polling.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()