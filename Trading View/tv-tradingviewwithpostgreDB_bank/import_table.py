import pandas as pd
from sqlalchemy import MetaData, exc
from sqlalchemy.orm import sessionmaker

from models.base import config, engine
from models.table_map import TableMap, create_table_map

schema = config.get('database', 'schema')
metadata = MetaData(schema=schema)


def import_table():
    tables = pd.read_csv('models/table_map.csv', skiprows=0)
    tables.dropna(inplace=True)
    mtable = []
    for data in tables.values:
        mtable.append(TableMap(data[0], data[1]))
    try:
        session.add_all(mtable)
        session.commit()
    except exc.SQLAlchemyError as err:
        print(err)


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
    create_table_map()
    import_table()
