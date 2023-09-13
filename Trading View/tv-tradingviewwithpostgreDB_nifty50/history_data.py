import threading
import _thread as thread
import asyncio
import print
import time
import websocket
import string
import random
import re
import logging
import requests
import json
from config.logging import setup_logging
from sqlalchemy import exc, and_, String, Column, Table, BIGINT, REAL, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from models.base import Abstract, Base, engine, config, metadata
from models.table_map import TableMap

max_get_data = config.getint('socket', 'max_get_data')
time_frame = config.get('socket', 'time_frame')


def on_message(wss, message):
    # if '"m":"du"' in message:
    #     logger.info('Data receive about prices in timeout:\n' + message)
    if 'timescale_update' in message:
        cs_session, symbol, btms = get_list_price_model_in_message(message)
        # Request more history data
        wss.send(generate_message('request_more_data', [cs_session, 's1', max_get_data]))
        logger.info('Data receive: ' + str(len(btms)) + ' data -> ' + symbol)
        if btms:
            # Case request more history data
            if len(btms) > 1:
                new_prices = filter_new_prices(btms, symbol)
                if new_prices:
                    logger.info('Saving data to DB')
                    save_data_to_db(wss, new_prices)
            # Case real-time by timeframe
            else:
                logger.info('Saving new data to DB')
                save_data_to_db(wss, btms)
        # else:
        #     logger.info('No new data => Close socket!!')
        #     wss.close()

    if re.search('~m~\\d+~m~~h~\\d+', message):
        logger.info('Send ping message: ' + message)
        wss.send(message)


def on_error(wss, error):
    logger.error('Connect socket error: ', error)
    wss.close()


def on_close(wss):
    logger.info("!!Socket close!!")
    wss.close()


def on_open(wss):
    wss.send(generate_message('set_auth_token', [config.get('socket', 'auth_token')]))


    def run():
        for symbol in symbols:
            cs = dict_session[symbol]['cs']
            wss.send(generate_message('chart_create_session', [cs]))
            if len(symbols) == 1:
                resolve_symbol = "={\"symbol\":\"" + symbol + "\",\"adjustment\":\"splits\"}"
            else:
                resolve_symbol = "={\"symbol\":\"" + symbol + "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"
            wss.send(generate_message('resolve_symbol', [cs, "symbol_1", resolve_symbol]))
            wss.send(generate_message('create_series', [cs, "s1", "s1", "symbol_1", time_frame, max_get_data]))
            logger.info('Send message get data ' + symbol + ' successfully')
            time.sleep(10)
    threading.Thread(target=run).start()


def save_data_to_db(wss, prices):
    try:
        session = Session()
        session.add_all(prices)
        session.commit()
        logger.info('Save {0} new data to DB successfully'.format(len(prices)))
    except exc.SQLAlchemyError as err:
        print(err)
        logger.error('An error occurred while saving data to DB')
        wss.close()
    except Exception as err:
        print(err)
        logger.error('An error occurred => Close socket')
        wss.close()


def generate_message(m, p):
    params = str({"m": m, "p": p}).replace(' ', '')
    if '"' in params:
        params = params.replace('"', '\\\"')
    params = params.replace("'", '"')
    package_symbols = config.get('symbol', 'package_symbols')
    data = [package_symbols, str(len(params)), package_symbols, params]
    return ''.join(data)


def get_list_price_model_in_message(message):
    data = list(filter(lambda dt: 'timescale_update' in dt, re.split('~m~\\d+~m~', message)))
    map_data = eval(data[0])
    p = map_data['p']
    cs_session = p[0]
    prices = p[1]['s1']['s']
    result = []
    symbol = get_symbol_by_cs_session(dict_session, cs_session)
    model = dict_session[symbol]['model']
    for price in prices:
        v = price['v']
        bm = model(name=symbol, time_frame=convert_time_frame(),
                   time=int(v[0]), open=v[1], high=v[2], low=v[3], close=v[4], vol=v[5])
        result.append(bm)
    return cs_session, symbol, result


def convert_time_frame():
    type_time = {
        '1': '1m', '3': '3m', '5': '5m', '10': '10m', '15': '15m', '30': '30m',
        '45': '45m', '60': '1h', '120': '2h', '180': '3h', '240': '4h'
    }
    return type_time.get(time_frame, time_frame)


def filter_new_prices(crawl_data, symbol):
    model = dict_session[symbol]['model']
    try:
        session = Session()
        db_times = set(dt[0] for dt in session.query(model).filter(and_(model.time_frame == convert_time_frame(),
                                                                        model.name == symbol)).values('time'))
    except exc.SQLAlchemyError as err:
        print(err)
    return list(filter(lambda price: price.time not in db_times, crawl_data))


def connect_wss_trading_view():
    wss = websocket.WebSocketApp(config.get('socket', 'url'), header=headers, on_message=on_message,
                                 on_error=on_error, on_close=on_close)
    wss.on_open = on_open
    wss.run_forever()

# Initialize the headers needed for the websocket connection
headers = json.dumps({
    # 'Connection': 'upgrade',
    # 'Host': 'data.tradingview.com',
    'Origin': 'https://data.tradingview.com'
    # 'Cache-Control': 'no-cache',
    # 'Upgrade': 'websocket',
    # 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    # 'Sec-WebSocket-Key': '2C08Ri6FwFQw2p4198F/TA==',
    # 'Sec-WebSocket-Version': '13',
    # 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
    # 'Pragma': 'no-cache',
    # 'Upgrade': 'websocket'
})


def get_auth_token():
    trading_view = config['tradingview']
    sign_in_url = trading_view['sign_in_url']
    username = trading_view['username']
    password = trading_view['password']
    data = {"username": username, "password": password, "remember": "on"}
    headers = {
        'Referer': trading_view['referer']
    }
    response = requests.post(url=sign_in_url, data=data, headers=headers)
    return response.json()['user']['auth_token']


def generate_session(type_session, length=12):
    letters = string.ascii_letters
    return type_session + '_' + ''.join(random.sample(letters, length))


def create_dict_of_symbol():
    result = {}
    session = Session()
    all_map_tables = session.query(TableMap).filter(TableMap.symbol.in_(symbols)).all()
    dict_model = {}
    for data in all_map_tables:
        table_name = data.table + '_raw' if time_frame.endswith('S') else data.table
        if table_name in dict_model:
            model = dict_model[table_name]
        else:
            model = type(string.capwords(table_name), (Abstract, Base), {"__tablename__": table_name})
            dict_model[table_name] = model
        result[data.symbol] = {'cs': generate_session('cs'), 'qs': generate_session('qs'),
                               'table': table_name, 'model': model}
    return result


def get_symbol_by_cs_session(dict_symbol, cs_session):
    for key in dict_session.keys():
        if dict_symbol[key]['cs'] == cs_session:
            return key


def create_price_tables():
    session = Session()
    table_names = session.query(TableMap.table.distinct()).all()
    for name in table_names:
        table_name = name[0] + '_raw' if time_frame.endswith('S') else name[0]
        Table(table_name, metadata,
              Column('name', String, primary_key=True),
              Column('time_frame', String, primary_key=True),
              Column('time', TIMESTAMP, primary_key=True),
              Column('open', REAL, nullable=False),
              Column('high', REAL, nullable=False),
              Column('low', REAL, nullable=False),
              Column('close', REAL, nullable=False),
              Column('vol', REAL, nullable=False))

    # Create table with check exist before
    metadata.create_all(bind=engine, checkfirst=True)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    # Create schema if not exist
    schema = config.get('database', 'schema')
    if not engine.dialect.has_schema(engine, schema):
        engine.execute(CreateSchema(schema))
    Session = sessionmaker(bind=engine)
    # Create table
    create_price_tables()
    # session = Session()

    symbols = set(re.sub(' +', '', config.get('socket', 'symbol')).split(','))
    dict_session = create_dict_of_symbol()

    # Connect websocket => get data
    connect_wss_trading_view()

