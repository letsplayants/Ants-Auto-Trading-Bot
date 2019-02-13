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
            json.dump(data, fp)
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

     
def add_exchange(config_file, new_exchange):
    #파일을 열어서 기존 설정을 읽어온다
    config = readKey(config_file)
    
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
        config[new_exchange] = key_set
        
        print(config)
        saveConf(config_file, config)
    except Exception as exp:
        print('except : {}'.format(exp))
        sys.exit(1)
    
def test_exchange(config_file, new_exchange):
    #파일을 열어서 기존 설정을 읽어온다
    config = readKey(config_file)
    
    try:
        pub_key = config['key_file']['rsa_pub_file']
        private_key = config['key_file']['rsa_key_file']
    
        data = config[new_exchange]['apiKey']
        borg = binascii.a2b_base64(data)
        apiKey = decrypt(private_key, borg)
        print(apiKey)
        
        data = config[new_exchange]['secret']
        borg = binascii.a2b_base64(data)
        secret = decrypt(private_key, borg)
        print(secret)
        
        
        #TODO ccxt를 사용하여 동작테스트를 한다
        
    except Exception as exp:
        print('except : {}'.format(exp))
        sys.exit(1)

if __name__ == "__main__":
    """
      crypt_cli add exchange --file config_file_name
      crypt_cli test exchange -f config_file_name
    """
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="add or test", choices=['add', 'test'])
    parser.add_argument("exchange", help="exchange name or ALL", default=None)
    parser.add_argument("-f", "--file", help="config file")
    args = parser.parse_args()
    
    args.exchange = args.exchange.upper()
    
    if(args.exchange == 'ALL'):
        print("Can't add exchange name 'ALL'")
        sys.exit(0)
    
    if(args.file):
        configFile = args.file
    else:
        configFile = 'configs/exchanges.conf'
        
    if(args.cmd == 'add'):
        print("got it", args.cmd)
        add_exchange(configFile, args.exchange)
    elif(args.cmd == 'test'):
        if(args.exchange == 'ALL'):
            test_exchange(configFile, 'ALL')
        else:
            test_exchange(configFile, args.exchange)
    
    pass