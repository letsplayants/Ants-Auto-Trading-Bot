#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse
import signal
import sys
import getpass
import os
import json
import base64
import binascii
import ccxt
from exchangem.database.sqlite_db import Sqlite

if __name__ == "__main__":
    """
      csvout.py trading --db data.db --output report20190220234433.csv
    """
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="add or test", choices=['trading','balance'])
    parser.add_argument("-d", "--db", help="sqlite3 db file")
    parser.add_argument("-o", "--output", help="output csv file name")
    args = parser.parse_args()
    
    #TODO 설정파일에서 읽어오도록 바꾼다
    # if(args.db):
    #     configFile = args.file
    # else:
    #     configFile = 'data.db'
        
    if(args.output):
        outputFile = args.output
    else:
        outputFile = None
        
    if(args.cmd == 'trading'):
        sq = Sqlite()
        sq.export_csv('trading',outputFile)
    
    pass