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
from read_api_key import readKey

EMAIL_SETTING = readKey('mail.key')

EMAIL_ACCOUNT = EMAIL_SETTING['id']
EMAIL_PASSWORD = EMAIL_SETTING['password']
# Use 'INBOX' to read inbox.  Note that whatever folder is specified, 
# after successfully running this script all emails in that folder 
# will be marked as read.
EMAIL_FOLDER = EMAIL_SETTING['folder']
EMAL_IMAP_SERVER = EMAIL_SETTING['imap_server']


def signal_handler(sig, frame):
    print('\nExit Program by user cause Ctrl + C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def process_mailbox(M):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    # rv, data = M.search(None, "ALL")
    rv, data = M.search(None, "SUBJECT", '"TradingView Alert"', '(UNSEEN)')
    if rv != 'OK':
        print("No messages found!")
        return

    print("total cnt : {}".format(data[0].split()))
    for msg_num in data[0].split():
        rv, data = M.fetch(msg_num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", msg_num)
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        
        subject = str(hdr)
        print('Message %s: %s' % (msg_num, subject))
        
        typ, data = M.store(msg_num, '+FLAGS', '\\Seen')
        if typ != 'OK':
            print('FLAGS setting error {}'.format(typ))
            return
        
        # print('Raw Date:', msg['Date'])
        
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            print ("Local Date:", \
                local_date.strftime("%a, %d %b %Y %H:%M:%S"))
                
    


M = imaplib.IMAP4_SSL(EMAL_IMAP_SERVER)


try:
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
except imaplib.IMAP4.error as exp:
    print ("LOGIN FAILED!!! {}".format(exp))
    sys.exit(1)

print(rv, data)

# rv, mailboxes = M.list()
# if rv == 'OK':
#     print("Mailboxes:")
#     print(mailboxes)

while(True) :
    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print("Processing mailbox...\n")
        process_mailbox(M)
    else:
        print("ERROR: Unable to open mailbox ", rv)

    time.sleep(10)  #입력값은 초단위이다. 10초마다 업데이트 확인함
    M.close()
    
M.logout()
print('program done!')