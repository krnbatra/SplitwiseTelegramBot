import logging

from splitwise import Splitwise
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
from commands import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

splitwise_object = Splitwise(CONSUMER_KEY, CONSUMER_SECRET)

commands = {  
    LIST_EXPENSE   : 'List expenses from your Splitwise account',
    SETTLE_EXPENESE : 'Settle expenses in your Splitwise account'
}

def initialize_bot(update):
    ''' initialze the splitwise object '''
    if update is not None:
        logger.info('User %s started the conversation.', update.message.from_user.first_name)
    access_token = {
        'oauth_token': OAUTH_TOKEN, 
        'oauth_token_secret': OAUTH_TOKEN_SECRET
    }
    splitwise_object.setAccessToken(access_token)
    logger.info('Splitwise Bot initalized!')

def help_callback(update, context):
    help_text = 'The following commands are available: \n'
    for command in commands:
        help_text += '" + command + ": '
        help_text += commands[command] + '\n'
    update.message.reply_text(help_text)  # send the generated help page

def list_expense_callback(update, context):
    initialize_bot(update)
    lend_output = 'OWES YOU:\n'
    borrow_output = 'YOU OWE:\n'
    friends = splitwise_object.getFriends()
    for friend in friends:        
        balances = friend.getBalances()
        if len(balances) > 0:
            print(friend.getFirstName(), friend.getLastName(), end = ' ')
            assert len(balances) == 1
            # output = f'{friend.getFirstName} {friend.getLastName()}'
            balance = float(balances[0].getAmount())
            if balance > 0:
                lend_output += f'\t\t{friend.getFirstName()} {friend.getLastName()}: ₹{balance}\n'
            else:
                borrow_output += f'\t\t{friend.getFirstName()} {friend.getLastName()}: ₹{abs(balance)}\n'
    output = lend_output + '\n\n' + borrow_output
    update.message.reply_text(output)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error) 

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(HELP, help_callback))
    dispatcher.add_handler(CommandHandler(LIST_EXPENSE, list_expense_callback))

    dispatcher.add_error_handler(error_callback)

    updater.start_polling()

if __name__ == '__main__':
    main()