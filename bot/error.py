# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext
from telegram import Update
# Helper methods import
from utils.logger import get_logger

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_error_handler(error)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
