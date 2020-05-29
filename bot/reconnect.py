import os

from bot.connect import connect
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
    dispatcher.add_handler(CommandHandler('reconnect', reconnect))


def reconnect(update: Update, context: CallbackContext):
    if is_spliwise_connected(update):
        key = str(update.effective_user.id)

        print_app_log(logger, update, f"Reconnecting user_id: {key}")
        redis.delete(key)

        update.message.reply_text(
            f"Successfully disconnected from your previous account.\n")
        connect(update, context)
        return
    else:
        print_app_log(
            logger, update, "Reconnecting to splitwise account, but the account is not connected")

        update.message.reply_text(f"Your account is not connected.\n"
                                  f"Run /connect to connect your Splitwise account.")
