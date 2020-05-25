from emoji import emojize
# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext
from telegram import Update
# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports
from telegram.ext import CommandHandler
from main import splitwise

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('start', start))


def start(update: Update, context: CallbackContext):
    try:
        tokens = context.args[0].split('-')

        # OAUTH_TOKEN, OAUTH_TOKEN_SECRET = tokens
        oauth_token, oauth_token_secret = tokens
        access_token = splitwise.getAccessToken(
            oauth_token, context.user_data['secret'], oauth_token_secret
        )
        # dictionary with oauth_token and oauth_token_secret as keys,
        # these are the real values for login purposes
        splitwise.setAccessToken(access_token)
        logger.info(
            f'APP: {update.effective_user.username}: Splitwise account connected successfully')
        update.message.reply_text(
            emojize("Splitwise account connected.\nNow manage your money effectively! :moneybag: ", use_aliases=True))
    except IndexError:
        logger.info(
            f'APP: {update.effective_user.username}: Started the conversation')
        update.message.reply_text(
            f"Your splitwise account is not connected. Please connect your account first")
