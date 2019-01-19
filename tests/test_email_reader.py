# -*- coding: utf-8 -*-
#!/usr/bin/env python
import unittest
import context
import sys
import os

import utils
import email_reader as email

#TradingView Alert: #BTCKRW #1M #SELL #BITHUMB

class EmailReaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        setting = utils.readKey('./configs/mail.key')
        EMAIL_ACCOUNT = setting['id']
        EMAIL_PASSWORD = setting['password']
        EMAIL_FOLDER = setting['folder']
        self.server = setting['imap_server']

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_login(self):
        m = email.conn()
        email.login(m)
        
    def test_parser(self):
        print(os.path.abspath('./tests'))
        dummy = utils.loadBinFile('./tests/email.sample')
        ret = email.parsingMsg(dummy)
        
        print(ret['market'][0:3])
        print(ret['market'][3:6])
        
        self.assertEqual(ret['market'], 'BTCKRW')
        self.assertEqual(ret['time'], '1M')
        self.assertEqual(ret['action'], 'SELL')
        self.assertEqual(ret['exchange'], 'BITHUMB')
        

if __name__ == '__main__':
    unittest.main()
    
    
    