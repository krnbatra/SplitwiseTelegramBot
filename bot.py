import configurations.settings as settings
import logging
import os

from functools import wraps
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
# from config import BOT_TOKEN, CONSUMER_KEY, CONSUMER_SECRET #, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
from commands import HELP, LIST_EXPENSE, SETTLE_EXPENESE, CREATE_EXPENSE, GET_NOTIFICATIONS, START, CONNECT, CANCEL

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

splitwise_object = Splitwise(
    os.environ.get("CONSUMER_KEY"), os.environ.get("CONSUMER_SECRET")
)

SETTLE_WITH_FRIEND = 'settle_with_friend'
CREATE_EXPENSE = 'create_expense'


commands = {
    CONNECT: 'Connects your Splitwise account',
    LIST_EXPENSE: 'List expenses from your Splitwise account',
    CREATE_EXPENSE: 'Create new expense in your Splitwise account',
    SETTLE_EXPENESE: 'Settle expenses in your Splitwise account'
}

AMOUNT, TYPING_REPLY, DESCRIPTION, SETTLE_WITH, CONFIRM = range(5)


OAUTH_TOKEN, OAUTH_TOKEN_SECRET = None, None


def connect(update, context):
    url, secret = splitwise_object.getAuthorizeURL()
    context.user_data['secret'] = secret
    update.message.reply_text(url)


def start(update, context):
    global OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    tokens = context.args[0].split('-')
    OAUTH_TOKEN = tokens[0]
    OAUTH_TOKEN_SECRET = tokens[1]
    logger.info('Secret', context.user_data['secret'])
    access_token = splitwise_object.getAccessToken(
        OAUTH_TOKEN, context.user_data['secret'], OAUTH_TOKEN_SECRET)
    # dictionary with oauth_token and oauth_token_secret as keys,
    logger.info(access_token)
    # these are the real values for login purposes
    splitwise_object.setAccessToken(access_token)


def help(update, context):
    help_text = '<b>The following commands are available:</b>\n\n'
    help_text += ''.join(
        [f'<b>{command}:</b> <i>{commands[command]}</i>\n' for command in commands])
    # send the generated help page
    update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def _initialize_bot(update):
    """ initialize the splitwise object """
    if update is not None:
        logger.info('User %s started the conversation.',
                    update.message.from_user.first_name)
    access_token = {
        'oauth_token': OAUTH_TOKEN,
        'oauth_token_secret': OAUTH_TOKEN_SECRET
    }
    splitwise_object.setAccessToken(access_token)
    logger.info('Splitwise Bot initalized!')


def _get_amount_from_friend(friend):
    return abs(float(friend.getBalances()[0].getAmount()))


def _get_friend_full_name(friend):
    first_name = friend.getFirstName()
    return f'{first_name} {friend.getLastName()}' if friend.getLastName() is not None else first_name


def _get_lend_expenses(friends_with_expenses):
    lend_output = '<b>OWES YOU:</b>\n'
    lend_output += ''.join(
        [f'{_get_friend_full_name(friend)}: ₹{_get_amount_from_friend(friend)}\n'
         for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) > 0])
    logger.debug(lend_output)
    return lend_output


def _get_borrowed_expenses(friends_with_expenses):
    borrow_output = '<b>YOU OWE:</b>\n'
    borrow_output += ''.join(
        [f'{_get_friend_full_name(friend)}: ₹{_get_amount_from_friend(friend)}\n'
         for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) < 0])
    logger.debug(borrow_output)
    return borrow_output


def _get_friends_with_expenses():
    friends_with_expenses = [friend for friend in splitwise_object.getFriends(
    ) if len(friend.getBalances()) > 0]
    logger.debug(friends_with_expenses)
    return friends_with_expenses


def _get_all_expenses():
    friends_with_expenses = _get_friends_with_expenses()
    output = _get_lend_expenses(
        friends_with_expenses) + '\n\n' + _get_borrowed_expenses(friends_with_expenses)
    return output


@send_typing_action
def list_expense(update, context):
    # _initialize_bot(update)

    output = _get_all_expenses()
    update.message.reply_text(output, parse_mode=ParseMode.HTML)


def _get_keyboard_layout(friends, column_size=2):
    keyboard = []
    row = []
    for friend in friends:
        name = f'{_get_friend_full_name(friend)}'
        row.append(InlineKeyboardButton(name, callback_data=friend.getId()))
        if len(row) == column_size:
            keyboard.append(row)
            row = []
    keyboard.append(row)
    return keyboard


def _get_id_name_mapping():
    friends = _get_friends_with_expenses()
    return {friend.getId(): f'{_get_friend_full_name(friend)}' for friend in friends}


def _get_id_amount_mapping():
    friends = _get_friends_with_expenses()
    return {friend.getId(): _get_amount_from_friend(friend) for friend in friends}


def create_expense(update, context):
    # _initialize_bot(update)

    friends = splitwise_object.getFriends()
    reply_markup = InlineKeyboardMarkup(
        _get_keyboard_layout(friends, column_size=3))

    update.message.reply_text(
        'Create new expense with',
        reply_markup=reply_markup
    )
    return AMOUNT


def take_amount_input(update, context):
    query = update.callback_query
    friend_id = int(query.data)

    _id_name_mapping = _get_id_name_mapping()
    name = _id_name_mapping[friend_id]
    context.user_data[CREATE_EXPENSE] = [friend_id, name]

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'Enter amount for expense with {name}'
    )
    return TYPING_REPLY


def received_amount_information(update, context):
    try:
        amount = float(update.message.text)
        if amount <= 0:
            raise ValueError
        context.user_data[CREATE_EXPENSE].append(amount)
        name = context.user_data[CREATE_EXPENSE][1]
        update.message.reply_text(f'Expense to be created with <b>{name}</b> with amount <b>₹{amount}</b>\n'
                                  f'Now enter the description for this expense', parse_mode=ParseMode.HTML)
        return DESCRIPTION
    except ValueError:
        update.message.reply_text(
            'Invalid amount specified. Amount should be a positive value!!!')
        return TYPING_REPLY


def received_description_information(update, context):
    description = update.message.text
    context.user_data[CREATE_EXPENSE].append(description)
    _, name, amount, description = context.user_data[CREATE_EXPENSE]
    update.message.reply_text(f'Expense to be created with <b>{name}</b> with amount <b>₹{amount}</b>'
                              f' and description <b>{description}</b>', parse_mode=ParseMode.HTML)
    text = 'Are you sure you want to proceed?'
    confirm(update, context, text, True)
    return CONFIRM


def confirm(update, context, text, new_message):
    keyboard = [
        [InlineKeyboardButton('Yes', callback_data='yes'),
         InlineKeyboardButton('No', callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if new_message is True:
        update.message.reply_text(text, reply_markup=reply_markup)
    else:
        query = update.callback_query

        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=reply_markup
        )


def settle_expense(update, context):
    # _initialize_bot(update)

    friends_with_expenses = _get_friends_with_expenses()
    borrowed_friends = [friend for friend in friends_with_expenses if float(
        friend.getBalances()[0].getAmount()) < 0]
    reply_markup = InlineKeyboardMarkup(_get_keyboard_layout(borrowed_friends))

    update.message.reply_text(
        'Settle with',
        reply_markup=reply_markup
    )
    return SETTLE_WITH


def settle_with_friend(update, context):
    query = update.callback_query
    friend_id = int(query.data)

    _id_name_mapping = _get_id_name_mapping()
    _id_amount_mapping = _get_id_amount_mapping()

    name = _id_name_mapping[friend_id]
    amount = _id_amount_mapping[friend_id]
    text = f'Settle balance with {name} of ₹{amount}?'
    confirm(update, context, text, False)
    return CONFIRM


def create_new_expense(update, context):
    logger.info("Creating expense!")
    query = update.callback_query
    friend_id, name, amount, description = context.user_data[CREATE_EXPENSE]

    self_id = splitwise_object.getCurrentUser().getId()
    create_expense_object(self_id, friend_id, amount, description)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='New expense created!'
    )


def create_settlement(update, context):
    logger.info("Settling the expense!")
    query = update.callback_query
    name, amount, friend_id = context.user_data[SETTLE_WITH_FRIEND]

    self_id = splitwise_object.getCurrentUser().getId()
    create_expense_object(self_id, friend_id, amount, 'Settling the expense')

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Expense settled!'
    )


def create_expense_object(payer_id, payee_id, amount, description):
    expense = Expense()
    expense.setCost(amount)
    expense.setDescription(description)

    payer = ExpenseUser()
    payer.setId(payer_id)
    payer.setPaidShare(amount)
    payer.setOwedShare(0.00)

    payee = ExpenseUser()
    payee.setId(payee_id)
    payee.setPaidShare(0.00)
    payee.setOwedShare(amount)

    users = [payer, payee]
    expense.setUsers(users)
    expense = splitwise_object.createExpense(expense)
    logger.info(expense)
    return expense


def cancel_expense(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='No expense updated'
    )


# TODO - find some way to store the last notification id and keep a job running which will check for new notifications
def get_notifications(update, context):
    # _initialize_bot(update)

    print(splitwise_object.getNotifications())


def unknown(update, context):
    update.message.reply_text(text="Sorry, I didn't understand that command.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def _get_conversation_handler(entry_points, states):
    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=[CommandHandler(CANCEL, cancel_expense)],
        allow_reentry=True,
        conversation_timeout=180
    )
    return conversation_handler


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(CONNECT, connect))
    dispatcher.add_handler(CommandHandler(START, start))
    dispatcher.add_handler(CommandHandler(HELP, help))
    dispatcher.add_handler(CommandHandler(LIST_EXPENSE, list_expense))

    list_conv_handler = _get_conversation_handler(
        entry_points=[CommandHandler(CREATE_EXPENSE, create_expense)],
        states={
            AMOUNT: [CallbackQueryHandler(take_amount_input)],
            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_amount_information),
                           ],
            DESCRIPTION: [MessageHandler(Filters.text,
                                         received_description_information), ],
            CONFIRM: [
                CallbackQueryHandler(create_new_expense, pattern='^yes$'),
                CallbackQueryHandler(cancel_expense, pattern='^no$')
            ]
        }
    )
    dispatcher.add_handler(list_conv_handler)

    settle_conv_handler = _get_conversation_handler(
        entry_points=[CommandHandler(SETTLE_EXPENESE, settle_expense)],
        states={
            SETTLE_WITH: [CallbackQueryHandler(settle_with_friend)],
            CONFIRM: [
                CallbackQueryHandler(create_settlement, pattern='^yes$'),
                CallbackQueryHandler(cancel_expense, pattern='^no$')
            ]
        }
    )
    dispatcher.add_handler(settle_conv_handler)

    # dispatcher.add_handler(CommandHandler(GET_NOTIFICATIONS, get_notifications_callback))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # log all errors
    dispatcher.add_error_handler(error)

    if settings.WEBHOOK:
        # signal.signal(signal.SIGINT, graceful_exit)
        updater.start_webhook(**settings.WEBHOOK_OPTIONS)
        updater.bot.set_webhook(url=settings.WEBHOOK_URL)
    else:
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
