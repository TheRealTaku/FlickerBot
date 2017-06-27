import asyncio
import logging
import os
import random
import signal
import sys
import traceback

import discord
from discord.ext import commands

from . import plugins
from .utils.config import Database

logger = logging.getLogger()
logger.setLevel(logging.INFO)
syslog = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s: %(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)


database = Database(database_url=os.getenv("DATABASE_URL"))


token = os.getenv('DISCORD_TOKEN')
email = os.getenv('DISCORD_EMAIL')
password = os.getenv('DISCORD_PASSWORD')
run_bot = os.getenv('RUN_BOT') or "TRUE"

if token is None:
    logger.critical("No TOKEN environment variable found, terminating")
    sys.exit(1)

if run_bot not in {"TRUE", "FALSE"}:
    logger.critical("No RUN_BOT environment variable not valid, must either be TRUE or FALSE, terminating")
    sys.exit(1)


client = commands.Bot([o[0] for o in database.retrieve_data_with_default('SETTINGS', column='prefix').fetchall()
                       if o[0] is not None], description='Flicker Bot')

UserID = None
UserName = None


@client.event
async def on_ready() -> None:
    global UserID, UserName
    UserID = client.user.id
    UserName = client.user.name
    logger.info('Logged in as %s, id: %s', UserName, UserID)


# @client.event
async def on_command_error(err: Exception, ctx: commands.Context) -> None:
    if hasattr(err, 'original'):
        logging.error(traceback.print_tb(err.original.__traceback__))
    else:
        logging.error(traceback.print_tb(err.__traceback__))
    if isinstance(err, commands.errors.CheckFailure):
        await client.send_message(ctx.message.channel, 'You don\'t have permission to use this command right now')


@client.event
async def on_message(message: discord.Message) -> None:
    logger.info("user: %s, channel: %s: %s", message.author.name, message.channel.name, message.content)

    if message.author.id == UserID:
        return
    if message.content.startswith('.die'):
        await client.send_message(message.channel, "I was.... bye ;(")
        sys.exit(0)
    elif message.content.startswith('.draw'):
        await client.send_message(message.channel, "Here's ur random number: %i" % random.randint(0, 100))
    else:
        await client.process_commands(message)


def main() -> None:
    logger.info('Starting up flicker_bot')
    plugins.load_plugins(client, db=database)

    loop = asyncio.get_event_loop()

    # login & start
    try:
        # catch SIGTERM and SIGKILL to exit properly
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(signum))
        if run_bot == 'TRUE':
            loop.run_until_complete(client.start(token))
        else:
            loop.run_until_complete(client.start(email, password, bot=False))
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(client.logout())
        logging.info("Logged out of account")
    finally:
        loop.close()
        logger.critical("Main thread has ended")

if __name__ == '__main__':
    main()
