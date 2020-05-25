# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext
from telegram import Update
# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports
from telegram.ext import CommandHandler

from main import splitwise_object

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('connect', connect))


def connect(update: Update, context: CallbackContext):
    logger.info(update)
    logger.info(
        f"APP: {update.effective_user.username}: Connecting to splitwise account")
    url, secret = splitwise_object.getAuthorizeURL()
    context.user_data['secret'] = secret
    update.message.reply_text(url)
