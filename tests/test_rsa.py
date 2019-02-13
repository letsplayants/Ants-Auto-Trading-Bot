# -*- coding: utf-8 -*-

import unittest
import sys
import os
import pkgutil

from Crypto.PublicKey import RSA
from exchangem.utils import Util


class CryptoTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.pub = Util.readKey('configs/ants.conf')['ras_pub_file']
        self.pri = Util.readKey('configs/ants.conf')['rsa_key_file']
        pass

    # def setUp(self):
        # self.bithumb = Bithumb(self.apiKey, self.apiSecret)

    def tearDown(self):
        pass
    
    def encrypt(self, msg):
        from Crypto.PublicKey import RSA
        from Crypto.Random import get_random_bytes
        from Crypto.Cipher import AES, PKCS1_OAEP
        
        data = "I met aliens in UFO. Here is the map.".encode("utf-8")
        
        with open(self.pub) as key:
            recipient_key = RSA.import_key(key.read())
            
        session_key = get_random_bytes(16)
        
        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        
        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        
        with open("encrypted_data.bin", "wb") as file_out:
            [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
        
    def decrypt(self, msg):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import AES, PKCS1_OAEP
        
        file_in = open("encrypted_data.bin", "rb")
        
        with open(self.pri) as key:
            private_key = RSA.import_key(key.read())
        
        enc_session_key, nonce, tag, ciphertext = \
           [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
        file_in.close()
        
        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        
        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        print(data.decode("utf-8"))

    def test_readRsaFile(self):
        self.encrypt('test')
        self.decrypt('test')
        
    
if __name__ == '__main__':
    unittest.main()
