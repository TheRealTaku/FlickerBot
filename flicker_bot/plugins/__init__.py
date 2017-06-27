from ..utils.plugins import ENABLED_PLUGINS
from ..utils.config import Database
from importlib import import_module
import logging

logger = logging.getLogger()


def load_plugins(client, db: Database = None) -> None:
    for plugin in ENABLED_PLUGINS:
        logger.info(f"Adding plugin: {plugin}")
        try:
            plugin = import_module(f".{plugin}", 'flicker_bot.plugins')
            plugin.run(client, db=db)
        except ModuleNotFoundError:
            logging.error(f"Plugin {plugin} not found")
        else:
            logging.info(f"Successfully added plugin: {plugin}")
