import discord
from discord.ext import commands

import logging
from typing import Union
from ..utils.plugins import Base
# from ..utils.check import owner_only
from ..utils.config import Database

logger = logging.getLogger()


class Currency(Base):
    database = Database(omit_logging=True)

    def __init__(self, client: Union[discord.Client, commands.Bot]):
        self.client = client
        super().__init__(Currency.database)

    def deposit(self, user: discord.User, amount: int) -> Union[int, bool]:
        """Deposit amount to the user, returns the original amount"""

        # check if amount is less than 1
        if amount < 1:
            return False

        result = self._manage(int(user.id), amount, operation='+', username=user.name)
        return result

    def withdraw(self, user: discord.User, amount: int) -> Union[int, bool]:
        """Withdraw amount from user, returns the original amount or False if failed"""

        # check if amount is less than 1
        if amount < 1:
            return False

        result = self._manage(int(user.id), amount, operation='-', username=user.name)
        return result

    # @owner_only(db=database)
    @commands.command(pass_context=True)
    async def add(self, ctx: commands.Context, amount: int):
        if self.deposit(ctx.message.author, amount):
            await self.client.send_message(ctx.message.channel, f"Added {amount} {self.get_cur(amount)} {self.cur_ico} "
                                                                f"to your account")
        else:
            await self.client.send_message(ctx.message.channel, f"Failed to add {amount} {self.get_cur(amount)}"
                                                                f" {self.cur_ico} to your account")

    @commands.command(pass_context=True)
    async def money(self, ctx: commands.Context):
        amount = self.balance(ctx.message.author)
        await self.client.send_message(ctx.message.channel, f"You have {amount} {self.get_cur(amount)} {self.cur_ico} "
                                                            f"in your account")

    # @owner_only(db=database)
    @commands.command(pass_context=True)
    async def take(self, ctx: commands.Context, amount: int):
        if self.withdraw(ctx.message.author, amount):
            await self.client.send_message(ctx.message.channel, f"Taken {amount} {self.get_cur(amount)} {self.cur_ico} "
                                                                f"to your account")
        else:
            await self.client.send_message(ctx.message.channel, f"Failed to take {amount} {self.get_cur(amount)}"
                                                                f" {self.cur_ico} from your account")


def run(client, db: Database = None):
    if db is not None:
        Currency.database = db
    client.add_cog(Currency(client))
