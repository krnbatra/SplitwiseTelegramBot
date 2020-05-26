from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from utils.logger import get_logger

# Init logger
logger = get_logger(__name__)


def get_keyboard_layout(splitwise, friends, column_size=2):
    keyboard = []
    row = []
    for friend in friends:
        name = f'{splitwise.get_friend_full_name(friend)}'
        row.append(InlineKeyboardButton(name, callback_data=friend.getId()))
        if len(row) == column_size:
            keyboard.append(row)
            row = []
    keyboard.append(row)
    return keyboard


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


def timeout(update, context):
    context.bot.edit_message_text(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id + 1,
        text='You took longer than expected. Please run the query again.'
    )


def done(update, context):
    context.bot.edit_message_text(chat_id=update.message.chat_id,
                                  message_id=update.message.message_id - 1,
                                  reply_markup=None,
                                  text="Can't update previous command")
    return ConversationHandler.END


def send_account_not_connected(update, context):
    logger.info(
        f"APP: {update.effective_user.username}: Splitwise account not connected")
    update.message.reply_text(
        "Your splitwise account is not connected.\nPlease connect your account first! ")
