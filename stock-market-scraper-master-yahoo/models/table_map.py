from models.base import Base, engine
from sqlalchemy import Column, String


def create_table_map():
    Base.metadata.create_all(engine, [TableMap.__table__], checkfirst=True)


class TableMap(Base):
    __tablename__ = 'table_map'
    symbol = Column(String, primary_key=True, nullable=False)
    table = Column(String, nullable=False)

    def __init__(self, symbol, table):
        self.symbol = symbol
        self.table = table


