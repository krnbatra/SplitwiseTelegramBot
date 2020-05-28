# Telegram API framework core imports
from telegram import InlineKeyboardMarkup, ParseMode
# Telegram API framework handlers imports
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import Dispatcher, Filters, CallbackQueryHandler

from main import splitwise
# Helper methods import
from utils.constants import ACCESS_TOKEN, NEW_EXPENSE, STATE_COMPLETE
from utils.helper import send_typing_action, get_keyboard_layout, confirm, timeout, done, send_account_not_connected
from utils.logger import get_logger, print_app_log

# Init logger
logger = get_logger(__name__)

TAKE_INPUT, TYPING_REPLY, CONFIRM = range(3)


class InvalidAmountError(ValueError):
    def __init__(self, amount):
        self.amount = amount


class InvalidDescriptionError(Exception):
    def __init__(self, description):
        self.description = description


def cancel_create_expense(update, context):
    print_app_log(logger, update, "Canceling the create expense")

    query = update.callback_query
    context.user_data[STATE_COMPLETE] = True
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='No expense created'
    )


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    create_handler = ConversationHandler(
        entry_points=[CommandHandler('create_expense', create_expense)],
        states={
            TAKE_INPUT: [CallbackQueryHandler(take_input)],
            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_input),
                           ],
            CONFIRM: [
                CallbackQueryHandler(create_new_expense, pattern='^yes$'),
                CallbackQueryHandler(cancel_create_expense, pattern='^no$')
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)],
        },
        fallbacks=[MessageHandler(Filters.command, done)],
        allow_reentry=True,
        conversation_timeout=30
    )
    dispatcher.add_handler(create_handler, 2)


def create_expense(update, context):
    try:
        if ACCESS_TOKEN not in context.user_data:
            raise Exception
        splitwise.setAccessToken(context.user_data[ACCESS_TOKEN])

        print_app_log(logger, update, "Initializing create expense")

        friends = splitwise.getFriends()
        reply_markup = InlineKeyboardMarkup(
            get_keyboard_layout(splitwise, friends, column_size=3))

        update.message.reply_text(
            'Create new expense with',
            reply_markup=reply_markup
        )
        return TAKE_INPUT
    except Exception:
        send_account_not_connected(update, context)


def take_input(update, context):
    print_app_log(logger, update,
                  "Waiting for user to enter input for creating expense")

    query = update.callback_query
    friend_id = int(query.data)

    _id_name_mapping = splitwise.get_id_name_mapping()
    name = _id_name_mapping[friend_id]
    context.user_data[NEW_EXPENSE] = [friend_id, name]

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'Enter amount and description for expense with <b>{name}.</b>\n'
             f'Use space to separate values.',
        parse_mode=ParseMode.HTML
    )
    return TYPING_REPLY


def received_input(update, context):
    try:
        query = update.callback_query
        amount, description = update.message.text.split(" ")
        try:
            amount = float(amount)
        except ValueError as e:
            raise InvalidAmountError(amount)

        if amount <= 0:
            raise InvalidAmountError(amount)

        if description is None or description == "":
            raise InvalidDescriptionError(description)

        print_app_log(
            logger, update, f"Input received correctly Amount: {amount}, Description: {description}")

        context.user_data[NEW_EXPENSE].extend([amount, description])
        id, name, amount, description = context.user_data[NEW_EXPENSE]
        update.message.reply_text(f'Expense to be created with <b>{name}</b> with amount <b>₹{amount}</b>'
                                  f' and description <b>{description}</b>', parse_mode=ParseMode.HTML)

        text = 'Are you sure you want to proceed?'
        confirm(update, context, text, True)
        return CONFIRM

    except InvalidAmountError as e:
        print_app_log(logger, update,
                      f"Invalid Amount: {e.amount} entered in create expense")

        update.message.reply_text(
            f"Invalid Amount: {e.amount} entered. Please input again.")
        return TYPING_REPLY

    except InvalidDescriptionError as e:
        print_app_log(logger, update,
                      f"Invalid Description: {e.description} entered in create expense")

        update.message.reply_text(
            f'Invalid Description: {e.description} entered in create expense. Please input again.'
        )
        return TYPING_REPLY

    except ValueError as e:
        # when only one string is provided
        print_app_log(logger, update,
                      f"Invalid input")

        update.message.reply_text(
            f'Invalid input. Please input again.\n\n'
            f'Valid Format:\n'
            f'Amount Description'
        )
        return TYPING_REPLY


@send_typing_action
def create_new_expense(update, context):
    query = update.callback_query
    friend_id, name, amount, description = context.user_data[NEW_EXPENSE]

    print_app_log(
        logger, update, f"creating new expense with {name}, of amount {amount} and description {description}")

    self_id = splitwise.getCurrentUser().getId()
    splitwise.create_expense_object(self_id, friend_id, amount, description)
    context.user_data[STATE_COMPLETE] = True
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='New expense created!'
    )
