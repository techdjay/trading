import time
import pymysql
import pickle
import zlib
import pandas as pd
pymysql.install_as_MySQLdb()
from sqlalchemy import (Table, MetaData, create_engine,Boolean,
                        Column, Integer, String, Float, SmallInteger, DateTime, JSON, PickleType)
from datetime import datetime
import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import logging
import threading

lock = threading.Lock()
logger = logging.getLogger(__name__)
Base = declarative_base()
# engine = create_engine("mysql+pymysql://root:123456@127.0.0.1/easycare?charset=utf8mb4", pool_size=100, max_overflow=50,
#                        pool_timeout=10)

engine = create_engine("mysql+mysqldb://root:Jayvns9807#@localhost/crypts?charset=utf8mb4", pool_size=100, max_overflow=20,
                       pool_timeout=10)
# engine = create_engine("mysql+mysqldb://root:xuanyutech@192.168.11.45:31646/scada?charset=utf8mb4", pool_size=100,max_overflow=20, pool_timeout=10)
# session_factory  = sessionmaker(bind=engine, autocommit=False)

session_factory = sessionmaker(bind=engine, autocommit=False)
session_maker = scoped_session(session_factory)



class Log(Base):
    __tablename__ = 'log'
    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column("name", String(20))
    tend = Column("tend", Boolean)
    index = Column("index",Float)
    tend_counter = Column("tend_counter",Integer)
    step_ratio = Column("step_ratio", Float)
    time = Column("time", DateTime)
    diff = Column("diff",Float)
    vote_step = Column("vote_step",Float)
    pch_step = Column("pch_step",Float)
    vote_cross = Column("vote_cross",Boolean)
    pch_cross = Column("pch_cross",Boolean)
    create_time = Column("create_time", DateTime, default=datetime.now)
    # cross = Column("cross", String(20))
    describe = Column("describe", String(1024))
    img = Column("img", String(54))
    email = Column("email",Integer)

class Crypts(Base):
    __tablename__ = 'crypts'
    id = Column("id", Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column("name", String(20))
    unit = Column("unit",String(20))
    time = Column("time", DateTime)
    open = Column("open",Float)
    close = Column("close",Float)
    high = Column("hign",Float)
    low = Column("low",Float)
    volume = Column("volume",Float)
    uniq = Column("uniq",Float,unique=True)
    create_time = Column("create_time",DateTime,default=datetime.now())




def insert_cryp(kwargs):
    try:
        session = session_maker()
        record = Crypts()
        record.name = kwargs.get("name")
        record.time = kwargs.get("time")
        record.close = kwargs.get("close")
        record.open = kwargs.get("open")
        record.high = kwargs.get("high")
        record.low = kwargs.get("low")
        record.volume = kwargs.get("volumefrom")
        record.unit = kwargs.get("unit")
        record.uniq = hash((kwargs.get("name"),kwargs.get("time")))
        session.add(record)
        # session.commit()
        session.commit()
        session.close()
        # print(f"insert fuck {kwargs.get('name')}")
    except Exception as e:
        logger.error(f"insert record error {repr(e)}")


def insert_warn(kwargs):
    try:
        session = session_maker()
        record = Log()
        record.name = kwargs.get("name")
        record.index = kwargs.get("index")
        record.tend = kwargs.get("tend")
        record.step_ratio = kwargs.get("step")
        record.pch_step = kwargs.get("pch_step")
        record.vote_step = kwargs.get("vote_step")
        record.vote_cross = kwargs.get("vote_cross",False)
        record.pch_cross = kwargs.get("cross_pch",None)
        record.time = kwargs.get("time")
        record.diff = kwargs.get("diff")
        record.tend_counter = kwargs.get("tend_counter")
        # record.cross = str(kwargs.get("vote_cross")) + str(kwargs.get("pch_cross"))
        record.describe = kwargs.get("describe")
        record.img = kwargs.get("img")
        record.email = int(kwargs.get("email",100))
        record.create_time = datetime.now()
        session.add(record)
        # session.commit()
        session.commit()
        session.close()
        # print(f"insert fuck {kwargs.get('name')}")
    except Exception as e:
        logger.error(f"insert record error {repr(e)}")


def get_warn(kwargs):
    try:
        session = session_maker()
        cursor = session.execute("""select * from (SELECT time,count(tend =0 or null) down, count(tend=1 or null) up from log  where email =1 and name like :delta and time >= :ct group by time) as a where a.down >=4 or a.up >=4""", {"delta":kwargs.get("delta"),"ct": kwargs.get("time")})
        result = cursor.fetchall()
        imgs = None
        if result:
            cursor = session.execute(
                """select name,img from log where name like :delta and email=1 and time = :rt""",
                {"delta": kwargs.get("delta"), "rt": result[-1][0]})
            imgs = cursor.fetchall()
        session.commit()
        session.close()
        return {kwargs.get("delta")[1:] + "@"  +str(bool((result[-1][2] - result[-1][1])>0)) +"@"+ result[-1][0].strftime("%Y%m%d%H%M%S"):{x[0]:"/blocks"+x[1].split("blocks")[-1] for x in imgs}} if imgs else None
    except Exception as e:
        print(repr(e))
        return None


def get_warn2(kwargs):
    try:
        session = session_maker()
        cursor = session.execute("""select * from (SELECT time,count(tend =0 or null) down, count(tend=1 or null) up from log  where email =1 and name like :delta and time >= :ct group by time) as a where a.down >=1 or a.up >=1""", {"delta":kwargs.get("delta"),"ct": kwargs.get("time")})
        result = cursor.fetchall()
        imgs = None
        df = pd.DataFrame(result, columns=["time", "down", "up"])
        t = []
        ts = kwargs.get("delta")[1:].split("X")
        minute = int(ts[0]) * int(ts[1])
        for i in range(1, df.shape[0]):
            item1 = df.loc[i - 1, :]
            x2 = df.loc[i, :]
            item2 = x2.copy()

            delta = item2["time"] - item1["time"]
            if item2["up"] >= 10 or item2["down"] >= 10:
                t.append(item2)
            elif delta.seconds <= minute * 60:
                if item1["up"] + item2["up"] >= 11 and item1["up"] >= 4 and item1["up"] < 10:
                    item2["up"] = item2["up"] + item1["up"]
                    t.append(item2)
                elif item1["down"] + item2["down"] >= 11 and item1["down"] >= 4 and item1["down"] < 10:
                    item2["down"] = item2["down"] + item1["down"]
                    t.append(item2)

        if t:
            cursor = session.execute(
                """select name,img from log where name like :delta and email=1 and time = :rt""",
                {"delta": kwargs.get("delta"), "rt": t[-1]["time"]})
            imgs = cursor.fetchall()
            if len(imgs) < max(t[-1]['up'],t[-1]["down"]):
                cursor = session.execute(
                    """select name,img from log where name like :delta and email=1 and time = :rt""",
                    {"delta": kwargs.get("delta"), "rt": t[-1]["time"] - dt.timedelta(seconds=minute*60)})
                jk=cursor.fetchall()
                imgs.extend(jk)
        session.commit()
        session.close()
        # if "30X4" in kwargs.get("delta"):
        #     print("fuck")
        return {kwargs.get("delta")[1:] + "@"  +str(bool((t[-1]['up'] - t[-1]['down'])>0)) +"@"+ t[-1]['time'].strftime("%Y%m%d%H%M%S"):{x[0]:"/blocks"+x[1].split("blocks")[-1] for x in imgs}} if imgs else None
    except Exception as e:
        print(repr(e))
        return None


def get_warn_group(kwargs):
    try:
        session = session_maker()
        cursor = session.execute("""select * from (SELECT time,count(tend =0 or null) down, count(tend=1 or null) up from log  where email =1 and name like :delta and time >= :ct group by time) as a where a.down >=1 or a.up >=1""", {"delta":kwargs.get("delta"),"ct": kwargs.get("time")})
        result = cursor.fetchall()
        session.commit()
        session.close()
        # return {kwargs.get("delta")[1:] + "@"  +str(bool((result[-1][2] - result[-1][1])>0)) +"@"+ result[-1][0].strftime("%Y%m%d%H%M%S"):{x[0]:"/blocks"+x[1].split("blocks")[-1] for x in result}} if result else None
        return result
    except Exception as e:
        print(repr(e))
        return None

