# -*- coding: utf-8 -*-
import logging
import sqlite3

#SQL Alchemy를 기반으로 작성한다. ORM인데 web은 나중에 flask로 작성한다.
#django는 자체 ORM을 가지고 있는데, 아직까지 굳이 장고를 꼭 써야하는 이유를 
#못 찾아서.. 조금 더 범용적인 SQL Alchemy를 사용한다

#https://www.sqlalchemy.org/library.html#architecture

class AntSQLite():
    pass


if __name__ == '__main__':
    print('AntSQLite test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    
    