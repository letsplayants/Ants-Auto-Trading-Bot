# -*- coding: utf-8 -*-
import sched, time

import threading
import logging
from datetime import datetime
from datetime import timedelta

import schedule

import ants.strategies.strategy
from ants.provider.observers import Observer
from ants.provider.email_provider import EmailProvider

from messenger.q_publisher import MQPublisher
from env_server import Enviroments

from exchangem.exchanges.upbit import Upbit as cUpbit


class Mail2QuickTradingStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    Email에 메일이 수신되면 텔레그램의 Quick Trading 포멧으로 던져준다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.telegram_messenger_exchange_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.messenger_q = MQPublisher(self.telegram_messenger_exchange_name)
        self.logger.debug('telegram message q name : {}'.format(self.telegram_messenger_exchange_name))
        self.exchanges = {}
        self.trading_cnt = 0
        self.add_exchange('upbit', cUpbit())

    def add_exchange(self, name, exchange):
        self.exchanges[name.upper()] = exchange
        
    def get_exchange(self, name):
        return self.exchanges[name.upper()]
    
    def run(self):
        #전략에서 사용할 데이터 제공자를 등록 후 실행
        self.data_provider = EmailProvider(True)
        self.data_provider.attach(self)
        self.data_provider.run()
        self.show_coin_has_show()
        self.logger.info('strategy run')

    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy : {}'.format(msg))
        # 텔레그램으로 메시지를 날려준다
        
        msg=msg[msg.find(':')+2:]
        
        try:
            #sell count 표시, 가격정보로 바꿔서 표시
            do, msg = self.check_signal(msg)
            if(do):
                # msg = msg + '\n' + add_msg
                self.messenger_q.send('{}'.format(msg))
            else:
                self.logger.debug('dont send to telegram')
        except Exception as exp:
            self.logger.warning(f'upate got error : {exp}')
        pass
    
    def stop(self):
        self.telegram.stop_listener()
        self.data_provider.stop()
        self.logger.info('Strategy will stop')

    def check_signal(self, msg):
        """
        세번째 buy일 경우 false
        그 외 true
        """
        text = msg.split(' ')
        
        command = text[0].strip().upper()
        exchange_name = text[1].strip().upper()
        market = text[2].strip().upper()
        coin_name = text[3].strip().upper()
        
        exchange = self.get_exchange(exchange_name)
        if(exchange is None):
            msg = '{} 이름이 유효하지 않습니다.'.format(exchange_name)
            self.logger.debug(msg)
            return False, msg
            
        fee = exchange.get_fee('krw')
        #항목 아래 함수가 자주 호출되면 block 걸린다
        symbol = '{}/{}'.format(coin_name, market)
        price = exchange.get_last_price(symbol)
        
        buy_info = self.get_state(exchange_name, coin_name, market)
        self.logger.debug('buy info : {}'.format(buy_info))
        if(buy_info == None):
            buy_cnt = 0
            b0 = price
            b1 = price
        else:
            buy_cnt = int(buy_info.get('buy_cnt')) if buy_info.get('buy_cnt') is not None else 0
            b0 = float(buy_info.get('1')) if buy_info.get('1') is not None else price
            b1 = float(buy_info.get('2')) if buy_info.get('2') is not None else price
            
        
        if(command == 'BUY'):
            if(buy_cnt >= 2):
                return False, '{}\n평균 구매 단가: {:,.2f}\n현재 2회 구매 중입니다\n추가 매입하지 않음\n'.format(coin_name, ((b0 + b1) / 2))
            
            if(buy_cnt == 0):
                price_msg = '1회차 구매 단가: {:,.2f}'.format(price)
            elif(buy_cnt == 1):
                price_msg = '1회차 구매 단가: {:,.2f}\n'.format(b0)
                price_msg += '2회차 구매 단가: {:,.2f}\n'.format(price)
                price_msg += '평균 구매 단가: {:,.2f}\n'.format((b0 + price) / 2)
            
            buy_cnt += 1
            self.trading_cnt += 1
            accumulate_profit = None
            
        elif(command == 'SELL'):
            buy_price = price #구매한적 없음
            if(buy_cnt == 0):
                return False, '구매한 적 없음'
                
            elif(buy_cnt == 1):
                buy_price = b0
            elif(buy_cnt == 2):
                buy_price = (b0 + b1) / 2
            
            try:
                accumulate_profit = buy_info['accumulate']
            except:
                accumulate_profit = 0
            
            sell_price = price
            profit_percent = ((sell_price - buy_price)  * 100) / buy_price - fee * 2 * 100
            accumulate_profit = accumulate_profit + profit_percent
            
            price_msg = '매수 단가 : {:,.2f}\n'.format(buy_price)
            price_msg += '매도 단가 : {:,.2f}\n'.format(sell_price)
            price_msg += '매매 수익률 : {:.2f}%\n'.format(profit_percent)
            price_msg += '누적 수익률 : {:.2f}%\n'.format(accumulate_profit)
            
            buy_cnt = 0
            
        self.save_state(exchange_name, coin_name, market, 'buy', buy_cnt, price, self.trading_cnt, accumulate_profit)
        
        command = text[0].strip().upper()
        exchange_name = text[1].strip().upper()
        market = text[2].strip().upper()
        coin_name = text[3].strip().upper()
        
        message = f'{command} {exchange_name} {market} {coin_name} {price} 100%\n'
        message += price_msg 
        
        return True, message
   
    def save_state(self, exchange, coin, market, action, buy_cnt, price, trading_cnt, accumulate=None):
        class_name = self.__class__.__name__.lower()
        exchange = exchange.lower()
        coin = coin.lower()
        market = market.lower()
        action = action.lower()
        
        # 기존 데이터를 읽어서 거기에 애드한다
        record_strategy = self.__get_dict__(Enviroments().strategies, class_name)
        record_exchange = self.__get_dict__(record_strategy, exchange)
        record_coin = self.__get_dict__(record_exchange, coin)
        record_market = self.__get_dict__(record_coin, market)
        
        if(accumulate != None):
            record_market['accumulate'] = accumulate
        if(buy_cnt != 0):
            record_market[str(buy_cnt)] = price
        record_market['buy_cnt'] = buy_cnt
        record_coin[market] = record_market
        record_exchange[coin] = record_coin
        record_exchange['trading_cnt'] = trading_cnt
        record_strategy[exchange] = record_exchange
        
        Enviroments().strategies[class_name] = record_strategy
        Enviroments().save_config()
        
    def __get_dict__(self, p, name):
        r = p.get(name)
        if(r == None):
         p[name] = {}
        
        return p[name]

    def get_state(self, exchange, coin, market):
        exchange = exchange.lower()
        coin = coin.lower()
        market = market.lower()
        
        try:
            class_name = self.__class__.__name__.lower()
            cnt = Enviroments().strategies[class_name][exchange][coin][market]
            return cnt
        except Exception as e:
            self.logger.debug('{} {}/{} has not states : {}'.format(exchange, coin, market, e))
            return None
   
    def get_bought_coin_list(self):
        exchange_name = 'upbit' #현재는 upbit만 있으므로~
        class_name = self.__class__.__name__.lower()
        coin_list = Enviroments().strategies[class_name][exchange_name]
        
        #TODO 거래한 모든 코인의 수익율을 보여주고
        #보유한 코인 목록만 리스팅 한다
        
        got_coin_list = []
        total_acc = 0
        buy_total_acc = 0
        message = '보유한 코인 목록 \n'
        
        exchange = self.get_exchange(exchange_name)
        if(exchange is None):
            msg = '{} 이름이 유효하지 않습니다.'.format(exchange_name)
            self.logger.debug(msg)
            return False, msg
        
        for coin in coin_list:
            if(coin == 'trading_cnt'):
                continue
            
            buy_info = coin_list.get(coin).get('krw')
            if(buy_info is not None):
                buy_cnt = int(buy_info.get('buy_cnt')) if buy_info.get('buy_cnt') is not None else None
                b0 = float(buy_info.get('1')) if buy_info.get('1') is not None else 0
                b1 = float(buy_info.get('2')) if buy_info.get('2') is not None else 0
                acc = float(buy_info.get('accumulate')) if buy_info.get('accumulate') is not None else 0
            if(buy_cnt == 1):
                buy_price = b0
            elif(buy_cnt == 2):
                #예외 상황 - b0이 0이거나 b1이 0일때가 있음
                buy_price = (b0 + b1) / 2
            
            #항목 아래 함수가 자주 호출되면 block 걸린다
            symbol = '{}/{}'.format(coin, 'krw').upper()
            price = exchange.get_last_price(symbol)
            profit_percent = ((price - buy_price)  * 100) / buy_price
            time.sleep(1) #가격 정보 받아오는 쿨다운..
            
            if(buy_cnt != 0):
                message += '{:5}\n누적 수익률: {:6.2f}%\n현재 수익률: {:6.2f}%\n\n'.format(coin.upper(), acc, profit_percent)
            else:
                message += '{:5}\n누적 수익률: {:6.2f}%\n\n'.format(coin.upper(), acc)
                
            total_acc += acc
            
        # message += '보유 중 코인들 수익률 : {:.2f}%\n'.format(buy_total_acc)
        message += '봇거래한 누적 수익률 : {:.2f}%'.format(total_acc)
        return message
        
    def __run__(self):
        self.report_every_time()
        # self.report_daily_report()
        
        # schedule.every(1).minutes.do(self.report_every_time)  #for test
        schedule.every().hour.at(":00").do(self.report_every_time)    #매시간마다 보고서를 출력한다
        schedule.every().day.at("15:00").do(self.report_daily_report)    #한국시간 밤 12시
        while True:
            schedule.run_pending()
            time.sleep(1)
        
    def show_coin_has_show(self):
        self.thread_hnd = threading.Thread(target=self.__run__, args=())
        self.thread_hnd.start()
        pass
    
    def report_every_time(self):
        msg = self.get_bought_coin_list()
        self.logger.debug('report time : {}'.format(msg))
        self.messenger_q.send('{}'.format(msg))
            
    def report_daily_report(self):
        #일일 보고서 쓰고, 결산하고 종료
        # 2019.06.05
        # 거래 횟수 : 100번
        # 누적 거래 수익률 : 45.55%
        # 코인별 누적 결과 :
        # BTC : 23.00%
        # ETH : -2.55%
        exchange_name = 'upbit' #현재는 upbit만 있으므로~
        class_name = self.__class__.__name__.lower()
        coin_list = Enviroments().strategies[class_name][exchange_name]
        trading_cnt = int(coin_list.get('trading_cnt')) if coin_list.get('trading_cnt') is not None else 0
        self.trading_cnt = 0
        coin_list['trading_cnt'] = 0
        
        
        got_coin_list = []
        total_acc = 0
        
        coin_msg = '코인별 누적 결과 :\n'
        for coin in coin_list:
            if(coin == 'trading_cnt'):
                continue
            
            buy_info = coin_list.get(coin).get('krw')
            if(buy_info is not None):
                acc = float(buy_info.get('accumulate')) if buy_info.get('accumulate') is not None else 0
                coin_list.get(coin)['krw']['accumulate'] = 0
                
            total_acc += acc
            coin_msg += '{} : {:.2f}%\n'.format(coin.upper(), acc)
            

        #날짜는 그냥 쓰도록 한다. 시스템 시간은 UTC 기준인데 한국 시간은 -9시간 해야한다
        #보고서가 출력되는 시간은 매일밤 자정이다
        #UTC시간으로 날짜가 변경되기 전이다.
        #그러므로 날짜는 그냥 쓰도록 한다.
        now = datetime.now()
        nowDate = now.strftime('%Y-%m-%d')
        
        message = f'{nowDate}\n'
        message += '거래 횟수 : {}\n'.format(trading_cnt)
        message += '누적 거래 수익률 : {}\n'.format(total_acc)
        message += coin_msg
        
        self.logger.debug(message)
        Enviroments().save_config()
        return message
        pass
   
if __name__ == '__main__':
    print('strategy test')
    
    import os
    path = os.path.dirname(__file__) + '/../../configs/ant_auto.conf'
    print('path : {}'.format(path))
    Enviroments().load_config(path)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("exchangem").setLevel(logging.ERROR)
    logging.getLogger("exchange").setLevel(logging.ERROR)
    
    
    s='TradingView Alert: sell upbit krw btc 0% 100%'
    s=s[s.find(':')+2:] #header 제거
    _list = s.split()
    print()
    
    
    test = Mail2QuickTradingStrategy()
    # test.run()
    
    # test.save_state('upbit','btc','krw','buy',0)
    # test.save_state('upbit','eth','krw','buy',1)
    # test.save_state('binance','eth','btc','buy',1)
    # test.save_state('binance','xrp','btc','buy',1)
    # test.save_state('bithumb','btc','krw','buy',1)
    
    # print('0번 구매 테스트')
    # msg ='sell upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do sell : {}'.format(add_msg))
    
    # print('한번 구매 테스트')
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do buy : {}'.format(add_msg))
    # msg ='sell upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do sell : {}'.format(add_msg))
    
    # print('두번 구매 테스트')
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do buy : {}\n\n'.format(add_msg))
    
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('2 do buy : {}\n\n'.format(add_msg))
    
    # msg ='sell upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do sell : {}'.format(add_msg))
    
    # print('세번 구매 테스트')
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do buy : {}\n\n'.format(add_msg))
    
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('2 do buy : {}\n\n'.format(add_msg))
    # msg ='buy upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(not do):
    #     print('3 do not buy : {}\n\n'.format(add_msg))
    
    # msg ='sell upbit krw btc 0% 100%'
    # do, add_msg = test.check_signal(msg)
    # if(do):
    #     print('1 do sell : {}'.format(add_msg))
    
    # s = sched.scheduler(time.time, time.sleep)
    # def do_something(sc): 
    #     print("Doing stuff...")
    #     # do your stuff
    #     s.enter(60, 1, do_something, (sc,))
    
    # s.enter(60, 1, do_something, (s,))
    # s.run()
    
    # ------------------------------------------------------------
    # def print_time(a='default'):
    #     print("From print_time", time.time(), a)
        
    # def print_some_times():
    #      print(time.time())
    #      s.enter(10, 1, print_time)
    #      s.enter(5, 2, print_time, argument=('positional',))
    #      s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
    #      s.run()
    #      print(time.time())
    # print_some_times()
    
    # ------------------------------------------------------------
    # s = sched.scheduler(time.time, time.sleep)
    # def run_every_time(cnt):
    #     print(time.time())
    #     cnt += 1
    #     if(cnt == 10):
    #         print('done')
    #         return
        
    #     s.enter(1, 1, run_every_time, (cnt,))
        
    # s.enter(1, 1, run_every_time, kwargs={'cnt': 0})
    # s.run()
        
    # test.show_coin_has_show()
    
    
    # #------------------------------------------
    # print('complex buy test')
    # msg ='buy upbit krw btc 0% 100%'
    # if(test.check_signal(msg)):
    #     print('BTC 1 do buy')
    
    # msg ='buy upbit krw eth 0% 100%'
    # if(test.check_signal(msg)):
    #     print('ETH 1 do buy')
        
    # msg ='buy upbit krw btc 0% 100%'
    # if(test.check_signal(msg)):
    #     print('BTC 2 do buy')
    
    # msg ='buy upbit krw btc 0% 100%'
    # if(test.check_signal(msg)):
    #     print('BTC 3 do buy')
    
    # msg ='sell upbit krw btc 0% 100%'
    # if(test.check_signal(msg)):
    #     print('BTC 1 do sell')
        
    # msg ='buy upbit krw eth 0% 100%'
    # if(test.check_signal(msg)):
    #     print('eth 2 do buy')
    
    # msg ='buy upbit krw eth 0% 100%'
    # if(test.check_signal(msg)):
    #     print('eth 3 do buy')
        
    # msg ='sell upbit krw eth 0% 100%'
    # if(test.check_signal(msg)):
    #     print('eth 1 do sell')
    
    # test.show_coin_has_show()
    # print(test.get_bought_coin_list())
    
    
    