import logging

from splitwise import Splitwise
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

commands = {  
    'list_expense'   : 'List expenses from your Splitwise account',
    'settle_expense' : 'Settle expenses in your Splitwise account'
}

def help_callback(update, context):
    help_text = "The following commands are available: \n"
    for command in commands:
        help_text += "/" + command + ": "
        help_text += commands[command] + "\n"
    update.message.reply_text(help_text)  # send the generated help page

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('help', help_callback))
    updater.start_polling()

if __name__ == '__main__':
    main()