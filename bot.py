import logging

from functools import wraps
from splitwise import Splitwise
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction

from config import BOT_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
from commands import HELP, LIST_EXPENSE, SETTLE_EXPENESE, CREATE_EXPENSE, GET_NOTIFICATIONS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

splitwise_object = Splitwise(CONSUMER_KEY, CONSUMER_SECRET)

commands = {  
    LIST_EXPENSE   : 'List expenses from your Splitwise account',
    SETTLE_EXPENESE : 'Settle expenses in your Splitwise account'
}

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

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
    help_text += ''.join([f"{command}: {commands[command]}\n" for command in commands])
    update.message.reply_text(help_text)  # send the generated help page

def _get_lend_expenses(friends_with_expenses):
    lend_output = 'OWES YOU:\n'
    lend_output += ''.join([f'\t\t{friend.getFirstName()} {friend.getLastName()}: ₹{friend.getBalances()[0].getAmount()}\n'
                            for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) > 0])
    logger.debug(lend_output)
    return lend_output

def _get_borrowed_expenses(friends_with_expenses):
    borrow_output = 'YOU OWE:\n'
    borrow_output += ''.join([f'\t\t{friend.getFirstName()} {friend.getLastName()}: ₹{friend.getBalances()[0].getAmount()}\n'
                            for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) < 0])
    logger.debug(borrow_output)
    return borrow_output

def _get_friends_with_expenses():
    friends_with_expenses = [friend for friend in splitwise_object.getFriends() if len(friend.getBalances()) > 0]
    logger.debug(friends_with_expenses)
    return friends_with_expenses

def _get_active_expenses_string():
    friends_with_expenses = _get_friends_with_expenses()
    output = _get_lend_expenses(friends_with_expenses) + '\n\n' + _get_borrowed_expenses(friends_with_expenses)
    return output

@send_typing_action
def list_expense_callback(update, context):
    initialize_bot(update)
    output = _get_active_expenses_string()
    update.message.reply_text(output)

def get_keyboard_layout(context):
    friends = splitwise_object.getFriends()
    keyboard = []
    row = []
    for friend in friends:
        balances = friend.getBalances()
        if len(balances) > 0 and float(balances[0].getAmount()) < 0:
            name = f'{friend.getFirstName()}  {friend.getLastName()}'
            row.append(InlineKeyboardButton(name, callback_data=friend.getId()))
            if len(row) == 2:
                keyboard.append(row)
                row = []
    keyboard.append(row)
    return keyboard

def settle_expense_callback(update, context):
    initialize_bot(update)
    reply_markup = InlineKeyboardMarkup(get_keyboard_layout(context))
    update.message.reply_text(
        'Settle with',
        reply_markup=reply_markup
    )

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_notifications_callback(update, context):
    initialize_bot(update)
    print(splitwise_object.getNotifications())

def unknown_callback(update, context):
    update.message.reply_text(text="Sorry, I didn't understand that command.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(HELP, help_callback))
    dispatcher.add_handler(CommandHandler(LIST_EXPENSE, list_expense_callback))
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('settle_expense', settle_expense)],
    #     states={
    #         PAYEE: [CallbackQueryHandler(get_payee)],
    #         CONFIRM: [
    #                     CallbackQueryHandler(create_settle, pattern='^yes$'),
    #                     CallbackQueryHandler(no_settlement_done, pattern='^no$')
    #                  ]
    #     },
    #     fallbacks=[CommandHandler('settle_expense', settle_expense)]
    # )
    
    # dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(CommandHandler(GET_NOTIFICATIONS, get_notifications_callback))
    dispatcher.add_handler(CommandHandler(SETTLE_EXPENESE, settle_expense_callback))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_callback))
    
    # log all errors
    dispatcher.add_error_handler(error_callback)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()