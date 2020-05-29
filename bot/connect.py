import os

# Telegram API framework core imports
from telegram import Update
# Telegram API framework handlers imports
from telegram.ext import CallbackContext, Dispatcher
from telegram.ext import CommandHandler

from main import splitwise, redis
# Helper methods import
from utils.helper import send_account_not_connected, is_spliwise_connected
from utils.logger import get_logger, print_app_log

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('connect', connect))


def connect(update: Update, context: CallbackContext):
    if is_spliwise_connected(update):
        print_app_log(
            logger, update, "Trying to connect, but the splitwise account is already connected")

        update.message.reply_text(
            f"You have already connected your Splitwise account.\n"
            f"Run /reconnect command if you want to connect to your account again.")
        return
    else:
        print_app_log(logger, update, "Connecting to splitwise account")

        url, secret = splitwise.getAuthorizeURL()
        context.user_data['secret'] = secret
        update.message.reply_text(url)
