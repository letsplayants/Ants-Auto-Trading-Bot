#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import base64
import binascii

"""
2019-04-03
crypto_cli를 참고하여 write부분을 업데이트해야함.
"""
class Crypto():
    def __init__(self):
        self.public_key = ''
        self.private_key = ''
        pass
    
    def readKey(self, filePath):
        result = self.__read_json_file(filePath)
    
        self.public_key = result['key_file']['rsa_pub_file']
        self.private_key = result['key_file']['rsa_key_file']
        
        return result
    
    def read_encrytion_file(self, filePath):
        return self.__read_json_file(filePath)
        
    def __read_json_file(self, filePath):
        if not os.path.isfile(filePath):
            print("File path {} does not exist. Exiting...".format(filePath))
            return None
        
        try:
            with open(filePath, 'r') as fp:
                result = json.load(fp)
        except Exception as exp:
            print("Can't load json : {}".format(exp))
            return None
    
        return result
        
    def saveConf(self, filePath, data):
        try:
            with open(filePath, 'w') as fp:
                fp.write(json.dumps(data, sort_keys=True, indent=4))
                
        except Exception as exp:
            print("Can't load json : {}".format(exp))
            return False
    
        return True
    
    def encrypt(self, msg):
        return self.__encrypt(self.public_key, msg)

    def __encrypt(self, key_file, msg):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_OAEP
        
        data = msg.encode("utf-8")
        
        with open(key_file) as key:
            recipient_key = RSA.import_key(key.read())
    
        # Encrypt the msg with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enmsg = cipher_rsa.encrypt(data)
        
        return enmsg
    
    def decrypt(self, msg):
        return self.__decrypt(self.private_key, msg)
        
    def __decrypt(self, key_file, msg):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_OAEP
        
        with open(key_file) as key:
            private_key = RSA.import_key(key.read())
        
        # Decrypt the msg with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        data = cipher_rsa.decrypt(msg)
        
        return data.decode("utf-8")

if __name__ == "__main__":
    print('test')
    cp = Crypto()
    keyset = cp.readKey('configs/ants.conf')
    print(keyset)
    
    msg = 'Test Message.. EnCryption && DeCryption Done?!'
    
    print(cp.decrypt(cp.encrypt(msg)))
    
    pass