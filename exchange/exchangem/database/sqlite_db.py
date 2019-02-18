#-*- coding: utf-8 -*-
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()



class Sqlite():
    def __init__(self):
        base_directory = os.getcwd() + '/'
        # print (os.getcwd())
        filePath = os.path.join(base_directory, 'data.db')
        print(filePath)
        self.engine = create_engine('sqlite:///' + filePath, convert_unicode=True, echo=True)
        self.session = scoped_session(sessionmaker(autocommit=False, 
            autoflush=False, bind=self.engine))
        Base.metadata.create_all(self.engine)

    def add(self, trading):
        self.session.add(trading)
        self.session.commit()

    def query(self, body):
        return self.session.query(body)

#Base.query = db_session.query_property()

#def init_db():
#	import models
#	Base.metadata.create_all(bind=engine)

#mysql+pymysql://test_user:test_user!@#$@127.0.0.1/test
#mysql+mysqldb://test_user:test_user!@#$@127.0.0.1/test
