from .config import Database

import os
import logging

import discord
from discord.ext import commands


logger = logging.getLogger()


def owner_only(*, db: Database = None) -> commands.check:
    """Check if the command was ran by a owner, use this as a decorator @owner_only() """
    return commands.check(lambda ctx, _db=db: owner_check(ctx.message, db=_db))


def owner_check(message: discord.Message, *, db: Database = None) -> bool:
    """Check if the command was ran by a owner, use this as a function owner_check(ctx.message) """
    database = db or Database(database_url=os.getenv("DATABASE_URL"))
    cur = database.retrieve_data('SETTINGS', column='owner')
    owners = tuple(o[0] for o in cur.fetchall() if o[0] is not None)
    result = message.author.id in owners
    logger.info(f'owner_checked returned {result} when checking {message.author.id} in possible owners {owners}')
    return result
