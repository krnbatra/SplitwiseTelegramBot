import os

from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser


class SplitwiseTelegramBot(Splitwise):
    def __init__(self):
        super().__init__(os.environ.get("CONSUMER_KEY"), os.environ.get("CONSUMER_SECRET"))

    def _get_amount_from_friend(self, friend):
        return abs(float(friend.getBalances()[0].getAmount()))

    def _get_friend_full_name(self, friend):
        first_name = friend.getFirstName()
        return f'{first_name} {friend.getLastName()}' if friend.getLastName() is not None else first_name

    def get_lend_expenses(self, friends_with_expenses):
        lend_output = '<b>OWES YOU:</b>\n'
        lend_output += ''.join(
            [f'{self._get_friend_full_name(friend)}: ₹{self._get_amount_from_friend(friend)}\n'
             for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) > 0]
        )
        return lend_output

    def get_borrowed_expenses(self, friends_with_expenses):
        borrow_output = '<b>YOU OWE:</b>\n'
        borrow_output += ''.join(
            [f'{self._get_friend_full_name(friend)}: ₹{self._get_amount_from_friend(friend)}\n'
             for friend in friends_with_expenses if float(friend.getBalances()[0].getAmount()) < 0]
        )
        return borrow_output

    def get_friends_with_expenses(self):
        friends_with_expenses = [
            friend for friend in self.getFriends() if len(friend.getBalances()) > 0
        ]
        return friends_with_expenses
