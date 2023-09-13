import configparser
from sqlalchemy import Column, String, REAL, BIGINT, TIMESTAMP, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

config = configparser.ConfigParser()
config.read('config/config.ini')
engine = create_engine(config.get('database', 'url'))
schema = config.get('database', 'schema')
metadata = MetaData(schema=schema)
Base = declarative_base(metadata=MetaData(schema=schema))


class Abstract(object):
    name = Column(String, primary_key=True)
    time_frame = Column(String, primary_key=True)
    time = Column(TIMESTAMP, primary_key=True)
    open = Column(REAL, nullable=False)
    high = Column(REAL, nullable=False)
    low = Column(REAL, nullable=False)
    close = Column(REAL, nullable=False)
    vol = Column('vol', REAL, nullable=False)

    def __init__(self, name, time_frame, time, open, high, low, close, vol):
        self.name = name
        self.time_frame = time_frame
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vol = vol
