import sys
import signal
import time
import logging

from pybithumb.client import Bithumb

import utils
import email_reader as email

M = None
bithumb = None
usageKRW = 0
logger = logging.getLogger(__name__)
actionState = 'READY'  #BUY, SELL, READY
tradingRecord = {}

tradingLogger = logging.getLogger('tradingLogger')
file_handler = logging.FileHandler('./logs/trading.log')
tradingLogger.addHandler(file_handler)

def signal_handler(sig, frame):
    logger.info('\nExit Program by user Ctrl + C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def init():
    global usageKRW
    
    keys = utils.readKey('./configs/bithumb.key')
    apiKey = keys['api_key']
    apiSecret = keys['api_secret']
    usageKRW = keys['usageKRW']     #구매에 사용할 금액
    logger.info('usageKRW : {}'.format(utils.krwFormat(usageKRW)))

    try:
        global bithumb
        bithumb = Bithumb(apiKey, apiSecret)
        M = email.conn()
        ret = email.login(M)
        email.clearMailBox(M)
        email.logout(M)
    except Exception as exp:
        logger.error(exp)
        sys.exit(1)
    
def start():
    M = email.conn()
    ret = email.login(M)
    if ret != 'OK' :
        logger.error(ret)
        sys.exit(1)
    
    while(True):
        email.openFolder(M)
        time.sleep(5)  #입력값은 초단위이다. 10초마다 업데이트 확인함
        mthList = email.mailSearch(M)
        msgList = email.getMailList(M, mthList)
        
        for msg in msgList:
            ret = email.parsingMsg(msg[0][1])
            if ret != {}:
                logger.info('doActoin :{}'.format(ret))
                doAction(ret)
                logger.info('actoin done')
                
        email.closeFolder(M)
    
    email.logout(M)
    
    logger.info('program done!')

def doAction(msg):
    global actionState
    
    exchange = msg['exchange'].upper()
    coinName = msg['market'][0:3].upper()
    market = msg['market'][3:6].upper()
    action = msg['action'].upper()
    
    if(actionState == action) :
        logger.info('Already {} state'.format(action))
        return
    
    actionState = action
    
    if(exchange == 'BITHUMB') :
        if(market != 'KRW') :
            logger.warning('{} has not {} market'.format(exchange,market))
        if(coinName != 'BTC') :
            logger.warning('{} is not support not')
            return
        
        if(action == 'BUY'):
            buy(coinName)
        elif(action == 'SELL'):
            sell(coinName)
            
    else :
        logger.warning('{} is not support!'.format(exchange))
        return

def buy(coinName):
    fee = bithumb.get_trading_fee()
    balance = bithumb.get_balance('BTC') #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
    
    if(balance[2] - balance[3] < usageKRW) :
        logger.warning('not enought KRW balance')
        return
    
    marketPrice = bithumb.get_current_price(coinName)
    marketPrice = (int)(marketPrice / 1000)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 다른 코인들도 주문 단위가 각각 있을 것이다.
    marketPrice = marketPrice * 1000
    orderCnt = usageKRW / marketPrice
    
    feePrice = orderCnt - orderCnt * fee
    logger.debug(fee)
    logger.debug(feePrice)
    
    logger.info('Buy Order - price : {}\tcnt:{}'.format(marketPrice, orderCnt))
    try:
        # desc = bithumb.buy_limit_order(coinName, marketPrice, orderCnt)
        desc = bithumb.buy_market_order(coinName, orderCnt) #시장가 매수 주문
        getTradingResult(desc)
    except Exception as exp:
        logger.warning('Error buy order : {}'.format(exp))
    
def sell(coinName):
    balance = bithumb.get_balance(coinName) #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
    marketPrice = bithumb.get_current_price(coinName)
    marketPrice = (int)(marketPrice / 1000)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 다른 코인들도 주문 단위가 각각 있을 것이다.
    marketPrice = marketPrice * 1000
    # orderCnt = keepCnt[coinName] - balance #keepCnt를 구현해야함.. 거래소별 유지해야하는 코인개수
    orderCnt = balance[0] - balance[1]  #코인 전량을 다 팔아버린다.
    
    logger.info('Sell Order - price : {}\tcnt:{}'.format(marketPrice, orderCnt))
    try:
        # desc = bithumb.sell_limit_order(coinName, marketPrice, orderCnt)
        desc = bithumb.sell_market_order(coinName, orderCnt) #시장가 매도 주문
        getTradingResult(desc)
    except Exception as exp:
        logger.warning('Error sell order : {}'.format(exp))
    
    
def getTradingResult(orderID):
    bithumb.get_order_completed()
    tradingLogger.info()
    
if __name__ == '__main__':
    init()
    