#!/usr/bin/env python
#
# Very basic example of using Python 3 and IMAP to iterate over emails in a
# gmail folder/label.  This code is released into the public domain.
#
# This script is example code from this blog post:
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
# This is an updated version of the original -- modified to work with Python 3.4.
#
# 참고
# https://docs.python.org/3/library/imaplib.html
# https://docs.python.org/3.7/library/imaplib.html
# https://github.com/python/cpython/tree/master/Lib/email
# https://www.programcreek.com/python/example/2875/imaplib.IMAP4_SSL
# https://stackoverflow.com/questions/2230037/how-to-fetch-an-email-body-using-imaplib-in-python
# https://stackoverflow.com/questions/2251977/python-imap-and-gmail-mark-messages-as-seen

import sys
import imaplib
import getpass
import email
import email.header
import datetime
import time
import signal
import utils
import json

EMAIL_SETTING = utils.readKey('./configs/mail.key')

EMAIL_ACCOUNT = EMAIL_SETTING['id']
EMAIL_PASSWORD = EMAIL_SETTING['password']
EMAIL_FOLDER = EMAIL_SETTING['folder']
EMAIL_IMAP_SERVER = EMAIL_SETTING['imap_server']

def signal_handler(sig, frame):
    print('\nExit Program by user Ctrl + C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def parsingMsg(data):
    # 샘플 확보용 코드
    # utils.saveBinFile('/tmp/email.sample',data)
    
    msg = email.message_from_bytes(data)
    hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
    
    subject = str(hdr)
    
    #subject ex) TradingView Alert: #BTCKRW #1M #SELL #BITHUMB
    
    _list = subject.split('#')
    ret={}
    ret['market'] = _list[1].strip()
    ret['time'] = _list[2].strip()
    ret['action'] = _list[3].strip()
    ret['exchange'] = _list[4].strip()
    
    return ret
    
def setFlag(M, msg_num, flag, value):
    typ, data = M.store(msg_num, '+FLAGS', '\\Seen')
    if typ != 'OK':
        print('FLAGS setting error {}'.format(typ))
        return

def getLocalTime(msg):
    # Now convert to local date-time
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        print ("Local Date:", \
            local_date.strftime("%a, %d %b %Y %H:%M:%S"))
        return 'No have time info'
        
    return local_date
    
def mailSearch(M):
    # rv, data = M.search(None, "ALL")
    rv, data = M.search(None, "SUBJECT", '"TradingView Alert"', '(UNSEEN)')
    if rv != 'OK':
        print("No messages found!")
        return
    
    return data[0].split()  #메일 id 리스트를 넘겨준다

def getMailList(M, mList):
    mailList=[]
    for msg_num in mList:
        rv, data = M.fetch(msg_num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", msg_num)
            pass
        
        mailList.append(data)
        setFlag(M, msg_num, '+FLAGS', '\\Seen')
        
    return mailList
    
    # msg = parsingMsg(data[0][1])
    # setFlag(M, msg_num, '+FLAGS', '\\Seen')
        

def conn():
    mailConn = None
    try:
        mailConn = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
    except Exception as exp:
        print("Connecting error : {}".format(exp))
        return mailConn
    
    return mailConn

def login(M):
    try:
        rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print('IMAP Login {},\t{}'.format(rv, data))
    except imaplib.IMAP4.error as exp:
        print ("LOGIN FAILED!!! {}".format(exp))
        return 'Failed : {}'.format(exp)
    return 'OK'

def openFolder(M):
    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        pass
    else:
        print("ERROR: Unable to open mailbox ", rv)
    
def getFolderList(M):
    rv, mailboxes = M.list()
    if rv == 'OK':
        print("Mailboxes:")
        print(mailboxes)

def closeFolder(M):
    M.close()

def logout(M):
    M.logout()

if __name__ == '__main__':
    M = conn()
    ret = login(M)
    if ret != 'OK' :
        print(ret)
        sys.exit(1)
    
    while(True):
        openFolder(M)
        time.sleep(10)  #입력값은 초단위이다. 10초마다 업데이트 확인함
        closeFolder(M)
    
    logout(M)
    
    print('program done!')