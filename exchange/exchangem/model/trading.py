# -*- coding: utf-8 -*-
# https://www.pythoncentral.io/sqlalchemy-orm-examples/
# https://edykim.com/ko/post/getting-started-with-sqlalchemy-part-1/

import logging
from datetime import datetime

import exchangem.database.sqlite_db
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Trading(Base):
    """
    coin_name, 코인 이름(BTC, ETH, XRP)
    market, 마켓 종류(WON, USDT, BTC, ETH, BNB)
    type 지정가 거래, 시장가 거래(limit/market)
    side 구매 판매(buy/sell)
    amount 매매 수량(float)
    price 매매 단가(float)
    params 특수 파라메터(거래소마다 다름)
    request_id 거래소에 요청 후 돌아오는 구분자, uuid형식도 있고 int형식도 있고 다양함, 이 형식에 포함되지 못하면 테이블을 따로 만들어서 연결하도록 한다
    exchange_name 거래소 이름
    time 매매 요청시간
    
    서칭 가능한 기능
    - 거래소별 매매 기록
    - 코인별 매매 기록
    - 날짜별 매매 기록
    
    """
    __tablename__ = 'trading'
    
    id = Column(Integer, primary_key=True)
    coin_name = Column(String(8))
    market = Column(String(8))
    type = Column(String(8))
    side = Column(String(4))
    amount = Column(Float(8))
    price = Column(Float(8))
    params = Column(String(50))
    time = Column(DateTime, default=datetime.utcnow)
    request_id = Column(String(50))
    exchange_name = Column(String(10))
    
    def __init__(self, coin_name, market, type, side, amount, price, params, time, request_id, exchange_name):
        self.coin_name = coin_name
        self.market = market
        self.type = type
        self.side = side
        self.amount = amount
        self.price = price
        self.params = params
        self.time = time
        self.request_id = request_id
        self.exchange_name = exchange_name
        
        self.logger = logging.getLogger(__name__)
        self.logger.info('{},{},{},{},{},{},{},{},{},{}'.format(coin_name, market, type, side, amount, price, params, time, request_id, exchange_name))
        pass


def init_db():
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///data.db', echo=False)
    Base.metadata.create_all(bind=engine)
    
init_db()

if __name__ == '__main__':
    print('test')
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("__main__").setLevel(logging.DEBUG)
    # logging.getLogger("ccxt").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    # import os
    # from sqlalchemy import create_engine
    # engine = create_engine('sqlite:///orm_in_detail.db', echo=True)

    sqlite = exchangem.database.sqlite_db.Sqlite()
    
    print('---------------------------------')

    # from sqlalchemy.orm import sessionmaker
    # session = sessionmaker()
    # session.configure(bind=engine)
    # Base.metadata.create_all(engine)

    print('---------------------------------')
    print('func : {}'.format(func.now()))
    print('datatime : {}'.format(datetime.now()))
    print('datatime : {}'.format(datetime.utcnow))

    coin_name = 'btc'
    market = 'WON'
    type = 'limit'
    side = 'buy'
    amount = 1.1
    price = 0.45
    params = str({})
    time = datetime.now()
    request_id = ''
    exchange_name = 'Test'
    
    tr = Trading(
                 coin_name,
                 market,
                 type,
                 side,
                 amount,
                 price,
                 params,
                 time,
                 request_id,
                 exchange_name)
    
    print('---------------------------------')
    # s = session()
    # s.add(tr)
    # s.commit()      
    print('---------------------------------')
    sqlite.add(tr)
                 
    coin_name = 'btc'
    market = 'WON'
    type = 'limit'
    side = 'sell'
    amount = 1.1
    price = 0.45
    params = ''
    time = datetime.now()
    request_id = ''
    exchange_name = 'Test'
    tr = Trading(
                 coin_name,
                 market,
                 type,
                 side,
                 amount,
                 price,
                 params,
                 time,
                 request_id,
                 exchange_name)

    sqlite.add(tr)
    
    # s = session()
    # s.add(tr)
    # s.commit()
    print('--------------------------------------')
    # sqlite.query(Trading).all()
    # print(s.query(Trading).all())
    
    # print(sqlite.query(Trading).all())
    
    # sqlite.close()
    
    sqlite.export_csv(Trading.__tablename__)