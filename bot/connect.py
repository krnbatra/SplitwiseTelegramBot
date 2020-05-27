# Telegram API framework core imports
from telegram import Update
# Telegram API framework handlers imports
from telegram.ext import CallbackContext, Dispatcher
from telegram.ext import CommandHandler

from main import splitwise
# Helper methods import
from utils.helper import send_account_not_connected
from utils.logger import get_logger

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('connect', connect))


def connect(update: Update, context: CallbackContext):
    try:
        logger.info(
            f"APP: {update.effective_user.username}: Connecting to splitwise account")

        url, secret = splitwise.getAuthorizeURL()
        context.user_data['secret'] = secret
        update.message.reply_text(url)
    except Exception:
        send_account_not_connected(update, context)
