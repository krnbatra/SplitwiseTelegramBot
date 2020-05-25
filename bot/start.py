from emoji import emojize
# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext
from telegram import Update
# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports
from telegram.ext import CommandHandler

from main import splitwise_object
from main import OAUTH_TOKEN, OAUTH_TOKEN_SECRET

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('start', start))


def start(update: Update, context: CallbackContext):
    try:
        global OAUTH_TOKEN, OAUTH_TOKEN_SECRET
        tokens = context.args[0].split('-')

        OAUTH_TOKEN, OAUTH_TOKEN_SECRET = tokens
        access_token = splitwise_object.getAccessToken(
            OAUTH_TOKEN, context.user_data['secret'], OAUTH_TOKEN_SECRET)
        # dictionary with oauth_token and oauth_token_secret as keys,
        # these are the real values for login purposes
        splitwise_object.setAccessToken(access_token)
        logger.info(
            f'APP: {update.effective_user.username}: Splitwise account connected successfully')
        update.message.reply_text(
            emojize("Splitwise account connected.\nNow manage your money effectively! :moneybag: ", use_aliases=True))
    except IndexError:
        logger.info(
            f'APP: {update.effective_user.username}: Started the conversation')
        update.message.reply_text(
            f"APP: {update.effective_user.username}: Your splitwise account is not connected.Please connect your account first")
