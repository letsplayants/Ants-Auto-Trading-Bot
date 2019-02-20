#-*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import exchangem.model.trading
import exchangem.model.tbl_balance

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Sqlite():
    def __init__(self):
        base_directory = os.getcwd() + '/'
        filePath = os.path.join(base_directory, 'data.db')
        print(filePath)
        self.engine = create_engine('sqlite:///' + filePath, convert_unicode=True, echo=True)
        self.session = scoped_session(sessionmaker(autocommit=False, 
            autoflush=False, bind=self.engine))
        Base.metadata.create_all(bind=self.engine)

    def add(self, trading):
        s = self.session()
        s.add(trading)
        s.commit()

    def query(self, body):
        return self.session.query(body)
        
    def close(self):
        self.session.close()
        pass
    
    def export_csv(self, model, fileName=None):
        # https://stackoverflow.com/questions/2952366/dump-csv-from-sqlalchemy
        # https://stackoverflow.com/questions/51549821/sqlalchemy-how-to-access-column-names-from-resultproxy-and-write-to-csv-header
        import csv
        result = self.engine.execute('select * from {}'.format(model))

        if(fileName == None):
            fileName = 'report_{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
        
        outfile = open(fileName, 'w', newline='')
        outcsv = csv.writer(outfile, delimiter=',')
        outcsv.writerow(result.keys())
        outcsv.writerows(result.fetchall())
        outfile.close()
        

# __tablename__
#Base.query = db_session.query_property()

#def init_db():
#	import models
#	Base.metadata.create_all(bind=engine)

#mysql+pymysql://test_user:test_user!@#$@127.0.0.1/test
#mysql+mysqldb://test_user:test_user!@#$@127.0.0.1/test
if __name__ == '__main__':
    print('test')
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("__main__").setLevel(logging.DEBUG)
    
    
    time = datetime.now()
    fileName = 'report_{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
    print(fileName)