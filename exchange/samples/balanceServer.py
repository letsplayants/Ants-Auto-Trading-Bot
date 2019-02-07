
import arbitJudge

import time
import subprocess
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import os
import platform
import random
# from selenium import webdriver


import arbitJudge

import upbitBrige
import bithumbBrige



import json
# j = json.loads('{"one" : "1", "two" : "2", "three" : "3"}')
# j = json.loads( '{"orderbook":[{"index":1,"price":100,"size":5},{"index":2,"price":100,"size":5}], "timestamp":123123123}' )


print('Python %s on %s' % (sys.version, sys.platform))

# randomPort = random.randrange(20000,30000)
randomPort = 37777

# def init():
#     global maintainCoin

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

class DoyeobServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.server_version = 'Apache Tomcat 9.0.7'
        self.sys_version = 'Ubuntu 17.10.1 '
        self.send_response(200)
        self.send_header('Developer', 'doyeob@kaist.ac.kr 010-3233-1224')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_fail_response(self):
        self.server_version = 'Apache Tomcat 9.0.7'
        self.sys_version = 'Ubuntu 17.10.1 '
        self.send_response(400)
        self.send_header('Developer', 'doyeob@kaist.ac.kr 010-3233-1224')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        # print("--------------------GET--------------------")
        # self.parse_request() .path

        # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.path = str(self.path)
        # print( self.path )
        self.path = self.path.split("?",maxsplit=1)[0]
        # print( self.path )
        # print( str(self.headers) )
        # self._set_response()
        if str(self.path) == '/getBalance' or str(self.path) == '/':
            # print( options )
            # returnJson = '{"result":"success", "userName":"' + options['userName'] + '"}'
            returnJson = '{"result":"success"}'
            self._set_response()
            self.wfile.write( returnJson.encode('utf-8') )

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=DoyeobServer, port=randomPort):
    # logging.basicConfig(level=logging.INFO)
    # server_address = ('', port)
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    server_class.base_path = web_dir

    try:
        print( 'Arbit5Server running port ' + str(port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    # logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    import _thread
    _thread.start_new_thread(run, ())

    while True:
        time.sleep(2)
        # print("UPBIT--------------------------------")
        global u_balance
        global b_balance

        u_balance = upbitBrige.get_full_balance( 'BTC' )
        print( u_balance )
        # print('');
        # print("BITHUMB--------------------------------")
        b_balance = bithumbBrige.get_full_balance( 'BTC' )
        print( b_balance )

        if b_balance is None or u_balance is None:
            print( 'balance is None' )
            continue


        # try:
        # except Exception as e:
        #     print('ERROR ', e)
        #     continue
