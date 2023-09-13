import time

import pymysql
import json
from core.DBUtils import Base
pymysql.install_as_MySQLdb()
from sqlalchemy import (Table, MetaData, create_engine,
                        Column, Integer, String, Float, SmallInteger, DateTime, JSON, PickleType)
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.mutable import MutableList

engine = create_engine("mysql+mysqldb://root:Jayvns9807#@localhost/crypts?charset=utf8mb4")
# engine = create_engine("mysql+mysqldb://root:xuanyutech@192.168.11.45:31646/scada?charset=utf8mb4")


if __name__ == "__main__":

    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False)
    session = Session()
    session.is_active
    # try:
    # except Exception as e:
    #     print(e)
    #     session.rollback()
    session.close()
