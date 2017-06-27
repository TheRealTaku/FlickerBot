import logging
from .config import Database
from psycopg2 import IntegrityError, InternalError
from typing import Union
import discord

ENABLED_PLUGINS = {"money", "game"}
logger = logging.getLogger()


class Base:
    def __init__(self, database: Database):
        self._database = database
        self.cur_ico = database.retrieve_data('settings', column='currency_sign', row=1).fetchone()[0]
        self.cur_name = database.retrieve_data('settings', column='currency_name', row=1).fetchone()[0]
        self.cur_plrname = database.retrieve_data('settings', column='currency_plrname', row=1).fetchone()[0]

    def get_cur(self, amount):
        return self.cur_name if amount <= 1 else self.cur_plrname

    def balance(self, user: discord.User) -> int:
        self._manage(user.id, amount=0, operation='+')
        return self._database.retrieve_data(table='currency', row_id='userid',
                                            row=user.id, column='amount').fetchone()[0]

    def _manage(self, userid: int, amount: int, operation: str, username: str = None) -> Union[bool, int]:
        """The base function for managing currency in and outtake of user"""

        logger.info(f"Updated currency for user {userid} {username}, operation {operation}, amount {amount}")

        # check if the userid exists, if not, create a user with 0 amount
        try:
            cur = self._database.retrieve_data(table='currency', row_id='userid', row=userid, column='id')
        except InternalError:
            self._database.reinit()
            cur = self._database.retrieve_data(table='currency', row_id='userid', row=userid, column='id')

        if not cur.fetchone():
            self._database.write_data("INSERT INTO currency (username, userid, amount) VALUES (?, ?, 0)",
                                      (username, userid))

        # check if an IntegrityError, ie. when amount < 0
        try:
            self._database.write_data(f"UPDATE currency SET amount=amount{operation}{amount} WHERE userid=?", (userid,))
        except IntegrityError:
            self._database.reinit()
            return False
        return amount
