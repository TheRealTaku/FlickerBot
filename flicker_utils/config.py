import logging
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flicker_utils import sql_app
logger = logging.getLogger()


class Database:

    def __init__(self, database_url: str, postgresql=True, test_server=False):
        if postgresql:
            self.engine = sqlalchemy.create_engine(database_url, echo=True)
        else:
            self.engine = sqlalchemy.create_engine(f'sqlite:///{database_url}', echo=True)
        if test_server:
            sql_app.Base.metadata.drop_all(self.engine)
        sql_app.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create(self, tablename: str, *args, **kwargs):
        Table = getattr(sql_app, tablename)
        row = Table(*args, **kwargs)
        self.session.add(row)
        self.session.commit()

    def retrieve(self, tablename: str, with_filter: bool = False, _filter=None, get: str = None):
        Table = getattr(sql_app, tablename)
        query = self.session.query(Table)
        if with_filter:
            _filter = [getattr(Table, key) == value for key, value in _filter.items()]
            query = query.filter(*_filter)
        result = query.all()
        if get is not None:
            return getattr(result, get)
        return result

    def clear_table(self, tablename: str):
        Table = getattr(sql_app, tablename)
        self.session.query(Table).delete()
        self.session.commit()
        return True
