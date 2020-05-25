# Telegram API framework core imports
from telegram.ext import Dispatcher, CallbackContext
from telegram import Update, ParseMode
# Helper methods import
from utils.logger import get_logger

# Telegram API framework handlers imports
from telegram.ext import CommandHandler

from commands import commands

# Init logger
logger = get_logger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CommandHandler('help', help))


def help(update: Update, context: CallbackContext):
    help_text = '<b>The following commands are available:</b>\n\n'
    help_text += ''.join(
        [f'<b>{command}:</b> <i>{commands[command]}</i>\n' for command in commands])
    # send the generated help page
    update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
