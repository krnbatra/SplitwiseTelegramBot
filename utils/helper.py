from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
