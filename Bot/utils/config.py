import psycopg2
import urllib.parse as urlparse

import logging
from typing import Union
import sqlite3


logger = logging.getLogger()
cursor = Union[psycopg2.extensions.cursor, sqlite3.Cursor]


class Database:
    """Connect to postgres database, if failed, uses sqlite3 to create local database"""

    def __init__(self, database_url: str = None, *, omit_logging: bool = False):
        if not omit_logging:
            logger.info("init the Database")
        if database_url is not None:
            logger.info("Using postgres database")
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(database_url)

            self.conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            self._type = 'postgres'

        else:
            if not omit_logging:
                logger.warning("No DATABASE_URL variable found (most likely not ran from heroku), using local database")
            self.conn = sqlite3.connect('database.db')
            self._type = 'sqlite3'

        self.cur = self.conn.cursor()
        self.gen_tables()
        self.validate_tables()

    def reinit(self):
        self.conn.commit()
        self.cur.close()
        self.cur = self.conn.cursor()

    def gen_tables(self) -> None:
        """Generates the necessary tables if they do not exist"""
        self.cur.execute("CREATE TABLE IF NOT EXISTS SETTINGS(id SERIAL, prefix TEXT, currency_name TEXT, "
                         " currency_plrname TEXT, currency_sign TEXT, owner TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS CURRENCY(id SERIAL,"
                         " username TEXT, userid BIGINT NOT NULL, amount INTEGER NOT NULL CHECK (amount >= 0))")
        self.conn.commit()

    def validate_tables(self) -> None:
        """Validates if the columns and data types are true, currently only works with postgres database"""
        # TODO add support for sqlite3 in the validate_tables function
        if self._type == 'postgres':
            gen = False

            self.cur.execute("SELECT column_name, data_type FROM information_schema.columns "
                             "WHERE table_name='settings'")

            if self.cur.fetchall() != [('id', 'integer'), ('prefix', 'text'), ('currency_name', 'text'),
                                       ('currency_plrname', 'text'), ('currency_sign', 'text'), ('owner', 'text')]:
                self.cur.execute("DROP TABLE settings")
                logger.error("Table settings does not match required format, dropping settings")
                gen = True

            self.cur.execute("SELECT column_name, data_type FROM information_schema.columns "
                             "WHERE table_name='currency'")

            if self.cur.fetchall() != [('id', 'integer'), ('username', 'text'),
                                       ('userid', 'bigint'), ('amount', 'integer')]:
                self.cur.execute("DROP TABLE currency")
                logger.error("Table currency does not match required format, dropping currency")
                gen = True
            if gen:
                self.gen_tables()

    def retrieve_data(self, table: str, **kwargs) -> cursor:
        row = kwargs.pop('row', None)
        col = kwargs.pop('column', None)
        row_id = kwargs.pop('row_id', 'id')
        if kwargs:
            raise ValueError(f"Unknown keyword args: {', '.join([key for key in kwargs.keys()])}")
        if row is None:
            self.cur.execute(f"SELECT {col} FROM {table}")
            return self.cur
        else:
            self.cur.execute(self.convsql(f"SELECT {col} FROM {table} WHERE {row_id}=?", self._type), (int(row), ))
            return self.cur

    def retrieve_data_with_default(self, table: str, **kwargs) -> cursor:
        cur = self.retrieve_data(table, **kwargs)
        if not cur.fetchone():
            if table.lower() == 'settings':
                self.clear_table(table)
                logger.warning("settings table empty, redoing the table")
                cur.execute("INSERT INTO settings (prefix, currency_name, currency_plrname, currency_sign) "
                            "VALUES ('$', 'candy', 'candies', '🍬')")
                self.conn.commit()
        self.cur = self.retrieve_data(table, **kwargs)
        return cur

    def retrieve_empty_id(self, table: str, column: str, limit: int = 1) -> cursor:
        self.cur.execute(f"SELECT id FROM {table} WHERE {column} IS NULL LIMIT {limit}")
        return self.cur

    def clear_table(self, table: str) -> None:
        if self._type == 'postgres':
            self.cur.execute(f"TRUNCATE TABLE {table}")
            self.cur.execute(f"ALTER SEQUENCE {table}_ID_SEQ RESTART WITH 1")
            self.conn.commit()
        else:
            self.cur.execute(f"DROP TABLE {table}")
            self.conn.commit()
            self.gen_tables()

    def write_data(self, sqlcommand: str, sqlargs: Union[list, tuple] = ()) -> cursor:
        self.cur.execute(self.convsql(sqlcommand, self._type), sqlargs)
        self.conn.commit()
        return self.cur

    @staticmethod
    def convsql(string: str, sql_type: str) -> str:
        if sql_type == 'postgres':
            return string.replace('?', '%s')
        elif sql_type == 'sqlite3':
            return string
        else:
            logger.error("Unknown sql database type, fail to convert sqlstring")
            return string
