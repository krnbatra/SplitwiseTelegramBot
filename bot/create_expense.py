# Telegram API framework core imports
from telegram import InlineKeyboardMarkup, ParseMode
# Telegram API framework handlers imports
from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackQueryHandler

from main import splitwise
from utils.helper import get_keyboard_layout, confirm
# Helper methods import
from utils.logger import get_logger

# Init logger
logger = get_logger(__name__)

TAKE_INPUT, TYPING_REPLY, CONFIRM = range(3)

NEW_EXPENSE = 'new_expense'


class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidAmountError(Error):
    pass


class InvalidDescriptionError(Error):
    pass


def cancel_expense(update, context):
    logger.info(
        f"APP: {update.effective_user.username}: Canceling the create expense")
    query = update.callback_query
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
                CallbackQueryHandler(cancel_expense, pattern='^no$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_expense)],
        allow_reentry=True,
        conversation_timeout=180
    )
    dispatcher.add_handler(create_handler)


def create_expense(update, context):
    try:
        logger.info(
            f"APP: {update.effective_user.username}: Starting the create expense method")
        friends = splitwise.getFriends()
        reply_markup = InlineKeyboardMarkup(
            get_keyboard_layout(splitwise, friends, column_size=3))

        update.message.reply_text(
            'Create new expense with',
            reply_markup=reply_markup
        )
        return TAKE_INPUT
    except:
        logger.info(
            f"APP: {update.effective_user.username}: Splitwise account not connected")
        update.message.reply_text(
            "Your splitwise account is not connected. Please connect your account first! ")


def take_input(update, context):
    logger.info(
        f"APP: {update.effective_user.username}: Taking amount and description input")
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
        amount, description = update.message.text.split(" ")
        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError

        if description is None or description == "":
            raise InvalidDescriptionError
        logger.info(
            f"APP: {update.effective_user.username}: Input received correctly")
        context.user_data[NEW_EXPENSE].extend([amount, description])
        # context.user_data[NEW_EXPENSE].append(description)
        id, name, amount, description = context.user_data[NEW_EXPENSE]
        update.message.reply_text(f'Expense to be created with <b>{name}</b> with amount <b>₹{amount}</b>'
                                  f' and description <b>{description}</b>', parse_mode=ParseMode.HTML)

        text = 'Are you sure you want to proceed?'
        confirm(update, context, text, True)
        return CONFIRM
    except (InvalidAmountError, TypeError) as e:
        logger.info(
            f"APP: {update.effective_user.username}: Invalid amount")
        update.message.reply_text(
            'Amount should be a positive value! Please input again.')
        return TYPING_REPLY
    except InvalidDescriptionError:
        logger.info(
            f"APP: {update.effective_user.username}: Invalid description")
        update.message.reply_text(
            'Description not specified! Please input again.'
        )
        return TYPING_REPLY
    except ValueError:
        # when one of amount and description is not specified
        logger.info(
            f"APP: {update.effective_user.username}: Invalid input")
        update.message.reply_text(
            'Invalid input. Please input again.'
        )
        return TYPING_REPLY


def create_new_expense(update, context):
    logger.info(
        f"APP: {update.effective_user.username}: Creating new expense!")
    query = update.callback_query
    friend_id, name, amount, description = context.user_data[NEW_EXPENSE]

    self_id = splitwise.getCurrentUser().getId()
    splitwise.create_expense_object(self_id, friend_id, amount, description)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='New expense created!'
    )
