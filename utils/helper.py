from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import ConversationHandler

from utils.constants import STATE_COMPLETE
from utils.logger import get_logger, print_app_log

from main import splitwise, redis

# Init logger
logger = get_logger(__name__)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


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
        text='You took longer than expected. Please run the command again.'
    )


def done(update, context):
    if STATE_COMPLETE in context.user_data and context.user_data[STATE_COMPLETE]:
        del context.user_data[STATE_COMPLETE]
        return ConversationHandler.END
    context.bot.edit_message_text(chat_id=update.message.chat_id,
                                  message_id=update.message.message_id - 1,
                                  reply_markup=None,
                                  text="Can not update previous command")
    return ConversationHandler.END


def send_account_not_connected(update, context):
    logger.info(
        f"APP: {update.effective_user.username}: Splitwise account not connected")

    update.message.reply_text(
        "Your splitwise account is not connected.\nPlease connect your account first! ")


def is_spliwise_connected(update):
    key = str(update.effective_user.id)

    print_app_log(
        logger, update, f"Command: {update.message.text} Checking for {key} in redis")

    return redis.hexists(key, 'oauth_token') and redis.hexists(key, 'oauth_token_secret')


def set_access_token(logger, update, context):
    key = str(update.effective_user.id)

    if is_spliwise_connected(update):
        print_app_log(logger, update, f"Found user_id: {key} in redis")

        splitwise.setAccessToken(redis.hgetall(key))
    else:
        print_app_log(logger, update,
                      f"Not able to found user_id: {key} in redis")
        raise Exception
