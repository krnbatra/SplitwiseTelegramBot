# Telegram API framework core imports
from telegram.ext import Dispatcher, MessageHandler, Filters

# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))


def unknown(update, context):
    update.message.reply_text(text="Sorry, I didn't understand that command.")
