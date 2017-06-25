import discord
from discord.ext import commands

from ..utils.config import Database
from ..utils.plugins import Base

import iron_cache
from requests.exceptions import HTTPError

import logging
from random import shuffle, random

import re
import asyncio
import pickle
import base64
from typing import Union

logger = logging.getLogger()


class Games(Base):
    database = Database(omit_logging=True)

    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__(Games.database)
        self.deck = ('Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King')
        self.suits = ('Hearts♥️', 'Diamonds♦', 'Spades️♣️', 'Clubs️♠')
        self.deck = [f"{c} of {suit}" for suit in self.suits for c in self.deck]
        self.trans_deck = {card: (i % 13 if 0 < i % 13 <= 10 else 10) for i, card in enumerate(self.deck, start=1)}
        self.cache = iron_cache.IronCache(name=str(random()))

    # TODO annotate all the functions:

    async def start_blackjack(self):
        game_deck = self.deck.copy()
        shuffle(game_deck)
        user_deck, game_deck = await self.deal(user_deck=[], game_deck=game_deck, deal_num=2)
        dealer_deck, game_deck = await self.deal(user_deck=[], game_deck=game_deck, deal_num=2)
        return user_deck, dealer_deck, game_deck

    async def result(self, ctx: commands.Context, win: bool, cus_msg: str = None):
        await asyncio.sleep(1)
        if win:
            await self.client.send_message(ctx.message.channel, cus_msg or 'Congratulations! You won!')
        else:
            await self.client.send_message(ctx.message.channel, cus_msg or 'Boo hoo, you lost! The dealer won!')
        self.cache.delete(key=ctx.message.channel.id)

    @staticmethod
    async def deal(user_deck: Union[list, tuple], game_deck: Union[list, tuple],
                   deal_num: int = 1, get_drew_card: bool = False) -> tuple:
        c = None
        for _ in range(deal_num):
            c = game_deck.pop()
            user_deck.append(c)
        if get_drew_card:
            return user_deck, game_deck, c
        return user_deck, game_deck

    async def get_sum(self, deck) -> tuple:
        value = sum(self.trans_deck[card] for card in deck)
        value2 = sum(self.trans_deck[card] if self.trans_deck[card] != 1 else 11 for card in deck)
        if value2 > 21:
            return tuple([value, ])
        elif value != value2:
            return value, value2
        return tuple([value, ])

    @staticmethod
    async def timeout_check(cache):
        if cache.value == 'Timeout':
            return True
        return False

    @staticmethod
    def loads(pklstr: Union[str, bytes]) -> tuple:
        if type(pklstr) == str:
            pklstr.encode('utf-8')
        return pickle.loads(base64.b64decode(pklstr))

    @staticmethod
    def dumps(pkllst: Union[list, tuple]) -> str:
        return base64.b64encode(pickle.dumps(pkllst)).decode('utf-8')

    async def check_blackjack(self, deck):
        value = await self.get_sum(deck)
        if any(val == 21 for val in value):
            return True
        elif any(val < 21 for val in value):
            return False
        return

    @commands.group(pass_context=True)
    async def blackjack(self, ctx: commands.Context):
        logger.info("Called blackjack")
        bet = re.match("blackjack *(\d+)$", str(ctx.command))
        if ctx.invoked_subcommand is not None:
            logger.info("Sub-command invoked")
            return

        # TODO create betting in blackjack
        elif bet is not None:
            bet = bet.groups()[0]

        elif str(ctx.command).strip() != 'blackjack':
            await self.client.send_message(ctx.message.channel, f"{str(ctx.command).strip()} is not a valid command")
            return

        try:
            cached = self.cache.get(key=ctx.message.channel.id)
            if await self.timeout_check(cached):
                await self.client.send_message(ctx.message.channel, "Your game has timed out, restarting")
                self.cache.delete(key=ctx.message.channel.id)
            else:
                await self.client.send_message(ctx.message.channel, "A game is already going in your channel")
                return
        except HTTPError:
            pass
        self.client.loop.call_later(120, lambda: self.cache.put(key=ctx.message.channel.id, value="Timeout"))

        user_deck, dealer_deck, game_deck = await self.start_blackjack()
        self.cache.put(key=ctx.message.channel.id,
                       value=self.dumps((user_deck, dealer_deck, game_deck)))
        await self.client.send_message(ctx.message.channel, f"Your cards are {' and '.join(user_deck)}")
        if await self.check_blackjack(user_deck):
            await self.client.send_message(ctx.message.channel, "21, blackjack!")
            await self.result(ctx=ctx, win=True)

    @blackjack.command(pass_context=True)
    async def hit(self, ctx: commands.Context):
        logger.info('hit called')
        try:
            cached = self.cache.get(key=ctx.message.channel.id)
            if await self.timeout_check(cached):
                await self.client.send_message(ctx.message.channel, "Your game has timed out.")
                self.cache.delete(key=ctx.message.channel.id)
                return
        except HTTPError:
            await self.client.send_message(ctx.message.channel, "There's no game going on in your channel")
            return
        user_deck_1, dealer_deck, game_deck = self.loads(cached.value)
        user_deck, game_deck, drew_card = await self.deal(user_deck=user_deck_1, game_deck=game_deck,
                                                          deal_num=1, get_drew_card=True)
        self.cache.put(key=ctx.message.channel.id,
                       value=self.dumps((user_deck, dealer_deck, game_deck)))
        await self.client.send_message(ctx.message.channel, f"You drew {drew_card}.\n"
                                                            f" Your cards are {', '.join(user_deck)}")
        result = await self.check_blackjack(user_deck)
        if result is None:
            await self.client.send_message(ctx.message.channel, "Your cards wer busted!")
            await self.result(ctx=ctx, win=False)
        elif result:
            await self.client.send_message(ctx.message.channel, "21, blackjack!")
            await self.result(ctx=ctx, win=True)

    @blackjack.command(pass_context=True)
    async def stand(self, ctx: commands.Context):
        logger.info('stand called')
        try:
            cached = self.cache.get(key=ctx.message.channel.id)
            if await self.timeout_check(cached):
                await self.client.send_message(ctx.message.channel, "Your game has timed out.")
                self.cache.delete(key=ctx.message.channel.id)
                return
        except HTTPError:
            await self.client.send_message(ctx.message.channel, "There's no game going on in your channel")
            return
        user_deck, dealer_deck, game_deck = self.loads(cached.value)
        value = await self.get_sum(dealer_deck)
        while max(value) < 17:
            dealer_deck, game_deck, card_drew = await self.deal(user_deck=dealer_deck, game_deck=game_deck,
                                                                deal_num=1, get_drew_card=True)
            await self.client.send_message(ctx.message.channel, f"The dealer drew {card_drew}")
            value = await self.get_sum(dealer_deck)
        await asyncio.sleep(1)
        await self.client.send_message(ctx.message.channel, f" The dealer's cards are {', '.join(dealer_deck)}")
        result = await self.check_blackjack(dealer_deck)
        if result is None:
            await self.client.send_message(ctx.message.channel, "The dealer's cards were busted!")
            await self.result(ctx=ctx, win=True)
        elif result:
            await self.client.send_message(ctx.message.channel, "21, blackjack!")
            await self.result(ctx=ctx, win=False)
        else:
            user_result = await self.get_sum(user_deck)
            if max(user_result) > max(value):
                await self.result(ctx=ctx, win=True)
            elif max(user_result) < max(value):
                await self.result(ctx=ctx, win=False)
            else:
                await self.result(ctx=ctx, win=False, cus_msg="The game was a tie...")


def run(client, db: Database = None):
    if db is not None:
        Games.database = db
    client.add_cog(Games(client))
