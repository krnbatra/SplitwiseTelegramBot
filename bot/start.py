from emoji import emojize
from telegram import Update, ParseMode
# Telegram API framework handlers imports
from telegram.ext import CommandHandler
# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext

from main import splitwise
from utils.constants import ACCESS_TOKEN
from utils.helper import send_account_not_connected
# Helper methods import
from utils.logger import get_logger, print_app_log

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
        context.user_data[ACCESS_TOKEN] = access_token

        print_app_log(logger, update,
                      "Splitwise account connected successfully")

        update.message.reply_text(
            emojize("Splitwise account connected.\nNow manage your money effectively! :moneybag: ", use_aliases=True))
    except IndexError:
        print_app_log(logger, update, "Started the conversation")

        update.message.reply_text(
            f"""
Hello <b>{update.effective_user.first_name}</b>!
Welcome to Splitwize Bot 🤖!
I'll be managing your Splitwise account.
Run /help command to check what all things I can do.
Run /connect command to connect your Splitwise account.
            """, parse_mode=ParseMode.HTML
        )
    except Exception:
        send_account_not_connected(update, context)
