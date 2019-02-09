# -*- coding: utf-8 -*-
import logging
from ants.provider.observers import Observer
from ants.performer.smart_trader import SmartTrader
from exchangem.exchangem.upbit import Upbit as cUpbit
# from exchangem.exchangem.bithumb import Bithumb as cBithumb

class EmailAlretStrategy(Observer):
    """
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.actionState = 'READY'  #BUY, SELL, READY
        self.trader = SmartTrader()
        
        self.upbit = Upbit({'key_file':'configs/upbit.key'})
        self.trader.add_exchange(upbit)
    
    def run(self):
        self.logger.info('strategy run')
        
        
    def register_data_provider(self, provider):
        self.data_provider = provider
        self.data_provider.attach(self)

    def __perform(self, obu):
        #obu을 사용하여 판정을 한다
        #판정 후 등록된 func를 호출한다
        self.logger.info('perform strategy')
        
    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy')
        self.do_action(msg)
        pass
    
    def stop(self):
        self.logger.info('Strategy will stop')
    
    def do_action(self, msg):
        print('msg')
        exchange = msg['exchange'].upper()
        coinName = msg['market'][0:3].upper()
        market = msg['market'][3:6].upper()
        action = msg['action'].upper()
        
        self.trader.trading(exchange, market, action, coinName)
        
        if(self.actionState == action) :
            self.logger.info('Already {} state'.format(action))
            return
        
        if(exchange == 'BITHUMB') :
            if(market != 'KRW') :
                self.logger.warning('{} has not {} market'.format(exchange,market))
            if(coinName != 'BTC') :
                self.logger.warning('{} is not support not')
                return
            
            actionComplete = False
            if(action == 'BUY'):
                actionComplete = self.buy(coinName)
            elif(action == 'SELL'):
                actionComplete = self.sell(coinName)
            
            if(actionComplete):
                actionState = action
            
            #쿨다운에 걸리는 것을 막기 위한 임시방편
            time.sleep(1)
        else :
            logger.warning('{} is not support!'.format(exchange))
            return
    
    def buy(self, coinName):
        global fee
        logger.info('Buy Order')
        
        balance = bithumb.get_balance('BTC') #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
        
        if(balance[2] - balance[3] < usageKRW) :
            logger.warning('not enought KRW balance')
            return False
        
        marketPrice = bithumb.get_current_price(coinName)
        marketPrice = (int)(marketPrice / 1000)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 다른 코인들도 주문 단위가 각각 있을 것이다.
        marketPrice = marketPrice * 1000
        orderCnt = usageKRW / marketPrice
     
        try:
            desc = bithumb.buy_market_order(coinName, orderCnt) #시장가 매수 주문
            
            #거래 결과 검사 루틴
            if(desc is None):
                logger.warning('Buy order was failed')
                return False
                
            if(desc['status'] != '0000'):
                logger.warning('Buy order was failed : {}'.format(desc))
                bot.sendMessage('Buy order was failed : {}'.format(desc))
                return False
            
            getTradingResult('BUY', desc, balance)
        except Exception as exp:
            logger.warning('Error buy order : {}'.format(exp))
            bot.sendMessage('Error buy order : {}'.format(exp))
            return False
        
        return True
        
    def sell(self, coinName):
        global fee
        balance = bithumb.get_balance(coinName) #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
        orderCnt = balance[0] - balance[1]  #코인 전량을 다 팔아버린다.
        
        logger.info('Sell Order')
        try:
            desc = bithumb.sell_market_order(coinName, orderCnt) #시장가 매도 주문
            
            #거래 결과 검사 루틴
            if(desc is None):
                logger.warning('Sell order was failed')
                return False
                
            if(desc['status'] != '0000'):
                logger.warning('Sell order was failed : {}'.format(desc))
                bot.sendMessage('Sell order was failed : {}'.format(desc))
                return False
            
            getTradingResult('SELL', desc, balance)
        except Exception as exp:
            logger.warning('Error sell order : {}'.format(exp))
            bot.sendMessage('Error sell order : {}'.format(exp))
            return False
        
        return True
        
    def getTradingResult(action, result, balance):
        # status	결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)	String
        # order_id	주문 번호	String
        # cont_id	체결 번호	Number (String)
        # units	체결(매수) 수량 (수수료 포함)	Number (String)
        # price	1Currency당 KRW 가격 (체결가)	Number (String)
        # total	매수 KRW (체결가)	Integer
        # fee	거래 수수료	Number (String)
        # {'status': '0000', 'order_id': '1548078639677728', 'data': [{'cont_id': '32762404', 'units': '0.0025', 'price': 3980000, 'total': 9950, 'fee': '14.93'}]}
        
        global startKRW
        totalProfit = balance[2] - startKRW
        
        logger.debug('TradingResult : {}', result)
        resultMessage = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(action,
                                                         result['status'],
                                                         result['data'][0]['units'],
                                                         result['data'][0]['price'],
                                                         result['data'][0]['total'],
                                                         result['data'][0]['fee'],
                                                         utils.krwFormat(totalProfit))
        
        tradingLogger.info(resultMessage)
        bot.sendMessage(resultMessage)

    
if __name__ == '__main__':
    print('strategy test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    msg = {'market': 'BTCKRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st = EmailAlretStrategy()
    st.do_action(msg)