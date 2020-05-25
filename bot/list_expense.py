from functools import wraps
# Telegram API framework core imports
from telegram.ext import CallbackContext, Dispatcher
from telegram import ChatAction, Update, ParseMode
# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports
from telegram.ext import CommandHandler

from main import splitwise

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('list_expense', list_expense))


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def get_all_expenses():
    friends_with_expenses = splitwise.get_friends_with_expenses()
    output = f'{splitwise.get_lend_expenses(friends_with_expenses)}' \
             f'\n\n{splitwise.get_borrowed_expenses(friends_with_expenses)}'
    return output


@send_typing_action
def list_expense(update: Update, context: CallbackContext):
    output = get_all_expenses()
    update.message.reply_text(output, parse_mode=ParseMode.HTML)
