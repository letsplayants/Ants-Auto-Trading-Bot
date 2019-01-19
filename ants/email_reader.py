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
import logging

logger = logging.getLogger(__name__)

EMAIL_SETTING = utils.readKey('./configs/mail.key')

EMAIL_ACCOUNT = EMAIL_SETTING['id']
EMAIL_PASSWORD = EMAIL_SETTING['password']
EMAIL_FOLDER = EMAIL_SETTING['folder']
EMAIL_IMAP_SERVER = EMAIL_SETTING['imap_server']

def signal_handler(sig, frame):
    logger.info('\nExit Program by user Ctrl + C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def parsingMsg(data):
    # 샘플 확보용 코드
    # utils.saveBinFile('/tmp/email.sample',data)
    
    msg = email.message_from_bytes(data)
    hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
    
    subject = str(hdr)
    
    logger.debug('subject : {}'.format(subject))
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
        logger.warning('FLAGS setting error {}'.format(typ))
        return
    logger.debug('{} is seen'.format(msg_num))

def getLocalTime(msg):
    # Now convert to local date-time
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        logger.info ("Local Date:", \
            local_date.strftime("%a, %d %b %Y %H:%M:%S"))
        return 'No have time info'
        
    return local_date
    
def mailSearch(M):
    # rv, data = M.search(None, "ALL")
    rv, data = M.search(None, '(UNSEEN)')
    if rv != 'OK':
        logger.info("No messages found!")
        return
    
    logger.debug('mail list : {}'.format(data[0].split()))
    
    return data[0].split()  #메일 id 리스트를 넘겨준다

def getMailList(M, mList):
    mailList=[]
    for msg_num in mList:
        rv, data = M.fetch(msg_num, '(RFC822)')
        if rv != 'OK':
            logger.warning("ERROR getting message", msg_num)
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
        logger.error("Connecting error : {}".format(exp))
        sys.exit(1)
    
    return mailConn

def login(M):
    try:
        rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        logger.info('IMAP Login {},\t{}'.format(rv, data))
    except imaplib.IMAP4.error as exp:
        logger.error("LOGIN FAILED!!! {}".format(exp))
        sys.exit(1)
        
    return 'OK'

def openFolder(M):
    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        pass
    else:
        logger.warning("ERROR: Unable to open mailbox ", rv)
    
def getFolderList(M):
    rv, mailBoxes = M.list()
    if rv == 'OK':
        logger.info("Mailboxes:\n{}".format(mailBoxes))

def closeFolder(M):
    M.close()

def logout(M):
    M.logout()

def clearMailBox(M):
    openFolder(M)
    logger.info('Mailbox clear')
    data = mailSearch(M)
    getMailList(M, data)
    closeFolder(M)
    

if __name__ == '__main__':
    M = conn()
    ret = login(M)
    if ret != 'OK' :
        logger.error(ret)
        sys.exit(1)
    
    while(True):
        openFolder(M)
        time.sleep(10)  #입력값은 초단위이다. 10초마다 업데이트 확인함
        closeFolder(M)
    
    logout(M)
    
    logger.info('program done!')