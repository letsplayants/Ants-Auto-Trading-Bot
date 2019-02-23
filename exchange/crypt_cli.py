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
import importlib

def readKey(filePath):
    if not os.path.isfile(filePath):
        print("File path {} does not exist. Will Create.".format(filePath))
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
        with open(filePath, 'w+') as fp:
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

def upper(input):
    return input.upper()

def test_exchange(config_file, output_file, new_exchange, coin_name=None):
    print('exchange connection test with key')
    
    try:
        # 거래소 클래스를 찾는다
        exchange_class_path = 'exchangem.exchanges.{}'.format(new_exchange)
        class_name = new_exchange
        class_name = upper(class_name[0]) + class_name[1:len(class_name)]
        exchange_setting_conf = 'configs/{}.conf'.format(new_exchange)
        print('load class {}\tconfig file : {}\tkey file: {}'.format(class_name, exchange_setting_conf, config_file))
        
        
        #사용할 전략을 만든다
        loaded_module = importlib.import_module(exchange_class_path)
        klass = getattr(loaded_module, class_name)
        exchange = klass({'private_key_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':exchange_setting_conf})
        print('Text exchange : {}'.format(klass))
        
        
        #코인별 잔고를 찍는다.
        #설정 파일에 설정된 코인의 잔고를 찍는다
        #해당 거래소에 입력된 코인이 없을 수도 있다.
        #이를 대비하여 거래소에 존재하는 코인이나 설정 파일에 설정된 내용을 
        #기반으로 잔고 및 가용 금액을 조회, 테스트 해야한다
        if(coin_name == None):
            coin_name = 'KRW'
            
        print(exchange.get_balance(coin_name).get_all())
        print('Availabel {} size : {}'.format(coin_name, exchange.get_availabel_size(coin_name)))
        
    except Exception as exp:
        print('except : {}'.format(exp))
        sys.exit(1)

if __name__ == "__main__":
    """
      crypt_cli add exchange --file rsa_config_file --output encrypt_file.key
      crypt_cli test exchange -f rsa_config_file -o encrypt_file.key
    """
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="add or test", choices=['add', 'test'])
    parser.add_argument("exchange", help="exchange name or ALL", default=None)
    parser.add_argument("-f", "--file", help="config file")
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("-c", "--coin", help="test coin name")
    args = parser.parse_args()
    
    if(args.exchange == '__ALL__'):
        print("Can't add exchange name '__ALL__'")
        sys.exit(0)
    
    if(args.file):
        configFile = args.file
    else:
        configFile = 'configs/ants.conf'
        
    if(args.output):
        outputFile = args.output
    else:
        outputFile = 'configs/exchanges.key'
        
    if(args.cmd == 'add'):
        add_exchange(configFile, outputFile, args.exchange)
    elif(args.cmd == 'test'):
        if(args.exchange == 'ALL'):
            test_exchange(configFile, outputFile, '__ALL__')
        else:
            test_exchange(configFile, outputFile, args.exchange, args.coin)
    
    pass