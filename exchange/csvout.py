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

def readKey(filePath):
    if not os.path.isfile(filePath):
        print("File path {} does not exist. Exiting...".format(filePath))
        sys.exit(1)
    
    try:
        with open(filePath) as fp:
            result = json.load(fp)
    except Exception as exp:
        print("Can't load json : {}".format(exp))
        sys.exit(1)

    return result
    
def saveConf(filePath, data):
    try:
        with open(filePath, 'w') as fp:
            fp.write(json.dumps(data, sort_keys=True, indent=4))
            
    except Exception as exp:
        print("Can't load json : {}".format(exp))
        sys.exit(1)


def encrypt(key_file, msg):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    
    data = msg.encode("utf-8")
    
    with open(key_file) as key:
        recipient_key = RSA.import_key(key.read())

    # Encrypt the msg with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enmsg = cipher_rsa.encrypt(data)
    
    return enmsg

def decrypt(key_file, msg):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    
    with open(key_file) as key:
        private_key = RSA.import_key(key.read())
    
    # Decrypt the msg with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    data = cipher_rsa.decrypt(msg)
    
    return data.decode("utf-8")

     
def add_exchange(config_file, output_file, new_exchange):
    #파일을 열어서 기존 설정을 읽어온다
    config = readKey(config_file)
    try:
        exchanges = readKey(output_file)
    except :
        exchanges = {}
        
    new_exchange = new_exchange.upper()

    try:
        pub_key = config['key_file']['rsa_pub_file']
        private_key = config['key_file']['rsa_key_file']

        key = getpass.getpass(prompt='input key :')
        secret = getpass.getpass(prompt='secret key :')
        
        encoded = base64.encodebytes(encrypt(pub_key, key))
        en_apiKey = encoded.decode('ascii')
        
        encoded = base64.encodebytes(encrypt(pub_key, secret))
        en_secret = encoded.decode('ascii')
        
        key_set = {
            'apiKey': en_apiKey,
            'secret': en_secret
        }
        exchanges[new_exchange] = key_set
        
        saveConf(output_file, exchanges)
        print('config file save done')
        
        try:
            test_exchange(config_file, output_file, new_exchange)
        except Exception as texp:
            print('Did not add new key. try again...')
            sys.exit(1)
        
    except Exception as exp:
        print('except : {}'.format(exp))
        sys.exit(1)
    
def test_exchange(config_file, output_file, new_exchange):
    print('exchange connection test with key')
    
    config = readKey(config_file)
    exchanges = readKey(output_file)
    new_exchange = new_exchange.upper()
    
    try:
        pub_key = config['key_file']['rsa_pub_file']
        private_key = config['key_file']['rsa_key_file']
        
        data = exchanges[new_exchange]['apiKey']
        borg = binascii.a2b_base64(data)
        apiKey = decrypt(private_key, borg)
        
        data = exchanges[new_exchange]['secret']
        borg = binascii.a2b_base64(data)
        secret = decrypt(private_key, borg)
        
        #TODO ccxt를 사용하여 동작테스트를 한다
        new_exchange = new_exchange.lower()
        exchange = None
        for id in ccxt.exchanges:
            if(id == new_exchange):
                type_exchange = getattr(ccxt, id)
                exchange = type_exchange({
                                'apiKey': apiKey,
                                'secret': secret,
                                })
            
        if(exchange == None):
            print('Can''t find exchange {}'.format(new_exchange))
            return

        try:
            exchange.fetch_balance()
        except Exception as texp:
            print('something is wrong : {}'.format(texp))
            return

        print('test pass')
    except Exception as exp:
        print('except : {}'.format(exp))
        sys.exit(1)

if __name__ == "__main__":
    """
      csvout.py trading --db data.db --output report20190220234433.csv
    """
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="add or test", choices=['trading'])
    parser.add_argument("-d", "--db", help="sqlite3 db file")
    parser.add_argument("-o", "--output", help="output csv file name")
    args = parser.parse_args()
    
    #TODO 설정파일에서 읽어오도록 바꾼다
    if(args.db):
        configFile = args.file
    else:
        configFile = 'data.db'
        
    if(args.output):
        outputFile = args.output
    else:
        outputFile = None
        
    if(args.cmd == 'trading'):
        sq = Sqlite()
        sq.export_csv('trading',outputFile)
    
    pass