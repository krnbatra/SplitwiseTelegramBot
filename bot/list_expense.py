from telegram import ChatAction, Update, ParseMode
# Telegram API framework core imports
from telegram.ext import CallbackContext, Dispatcher
# Telegram API framework handlers imports
from telegram.ext import CommandHandler

from main import splitwise
from utils.constants import ACCESS_TOKEN
from utils.helper import send_typing_action, send_account_not_connected
# Helper methods import
from utils.logger import get_logger

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('list_expense', list_expense))


def get_all_expenses():
    friends_with_expenses = splitwise.get_friends_with_expenses()
    logger.info(
        f"APP: In get all expenses friends calculations")
    output = f'{splitwise.get_lend_expenses(friends_with_expenses)}' \
             f'\n\n{splitwise.get_borrowed_expenses(friends_with_expenses)}'
    return output


@send_typing_action
def list_expense(update: Update, context: CallbackContext):
    try:
        if ACCESS_TOKEN not in context.user_data:
            raise Exception
        splitwise.setAccessToken(context.user_data[ACCESS_TOKEN])

        logger.info(
            f"APP: {update.effective_user.username}: Listing all expenses")
        output = get_all_expenses()
        update.message.reply_text(output, parse_mode=ParseMode.HTML)
    except Exception:
        send_account_not_connected(update, context)
