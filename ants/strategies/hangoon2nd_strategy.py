# -*- coding: utf-8 -*-
import sched, time

import threading
import logging
from datetime import datetime, timedelta
import pytz

from apscheduler.schedulers.background import BackgroundScheduler

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
        self.each_coin_total_buy_cnt = {}
        self.each_coin_total_sell_cnt = {}
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
        self.shedule_start()
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
                self.logger.debug('dont send to telegram : {}'.format(msg))
        except Exception as exp:
            # https://api.telegram.org/bot 연결 테스트 후 결과도 함께 출력
            self.logger.warning(f'update got error : {exp}')
        pass
    
    def stop(self):
        self.thread_run = False
        self.shedule_stop()
        self.thread_hnd.join()
        self.telegram.stop_listener()
        self.data_provider.stop()
        self.logger.info('Strategy will stop')

    def parsing(self, msg):
        msg = msg.upper().split('#')
        msg = msg[1:]
        self.logger.debug(msg)
        
        ver = None
        for item in msg:
            ver = item.split(':')[0].upper().strip()
            if(ver == 'VER'):
                ver = item.split(':')[1].strip()
                break
            
        if(ver == None):
            msg = 'can''t find version information'
            self.logger.debug(msg)
            raise Exception(msg)
        
        if(ver == '1'):
            return self.parsing_v1(msg)
        
        msg = f'This version:({ver}) is not support'
        self.logger.debug(msg)
        raise Exception(msg)
            
    def parsing_v1(self, msg):
        """
        {
            'AUTO':True,
            'EXCHANGE':'upbit',
            'COIN':'BTC',
            'MARKET':'KRW',
            'TYPE':'LIMIT',
            'SIDE':'BUY',
            'RULE':'TSB',
            'TSB-MINUTE':'15m'
            'TSB-VER':'3.3'
        }
        """
        result = {}
        for item in msg:
            try:
                item = item.strip() #공백 제거
                item = item.split(':')
                result[item[0].lower()]=item[1].upper()
            except Exception as exp:
                self.logger.warning('message parsing error : {}'.format(exp))
                raise exp
            
        c = result['ver']
        c = result['auto']
        c = result['exchange']
        c = result['coin']
        c = result['market']
        if(result.get('type') is None):
            result['type'] = 'limit'
        c = result['type']
        c = result['side']
        c = result['rule']
        
        return result
        
    def check_signal(self, msg):
        """
        세번째 buy일 경우 false
        그 외 true
        
        msg 포멧은 다음과 같다
        헤더간 구분은 #을 사용한다
        헤더와 데이터는 :를 사용하여 구분한다
        대소문자를 가리지 않는다.
        커스텀 헤더가 붙을 수 있다
        
        #AUTO:0
        #VER:1
        #EXCHANGE:upbit
        #coin:btc
        #market:krw
        #type:limit
        #side:buy
        #rule:tsb
        --------아래로는 전략에 따른 커스텀 헤더-------------
        #tsb-minute:15
        """
        order = self.parsing(msg)
        
        command = order['side'].upper()
        exchange_name = order['exchange']
        market = order['market']
        coin_name = order['coin']
        
        exchange = self.get_exchange(exchange_name)
        if(exchange is None):
            msg = '{} 이름이 유효하지 않습니다.'.format(exchange_name)
            self.logger.debug(msg)
            return False, msg
            
        fee = exchange.get_fee('krw')
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
            
            price_msg = '{}\n{}\n'.format('-'*70, symbol)
            
            if(buy_cnt == 0):
                price_msg += '1회차 구매 단가: {:,.2f}'.format(price)
            elif(buy_cnt == 1):
                price_msg += '1회차 구매 단가: {:,.2f}\n'.format(b0)
                price_msg += '2회차 구매 단가: {:,.2f}\n'.format(price)
                price_msg += '평균 구매 단가: {:,.2f}\n'.format((b0 + price) / 2)
            
            buy_cnt += 1
            total_cnt = self.each_coin_total_buy_cnt.get(coin_name.lower(), 0)
            self.each_coin_total_buy_cnt[coin_name.lower()] = total_cnt + 1
            
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
            
            price_msg = '{}\n{}\n'.format('-'*70, symbol)
            price_msg += '매수 단가 : {:,.2f}\n'.format(buy_price)
            price_msg += '매도 단가 : {:,.2f}\n'.format(sell_price)
            price_msg += '매매 수익률 : {:.2f}%\n'.format(profit_percent)
            price_msg += '누적 수익률 : {:.2f}%\n'.format(accumulate_profit)
            
            buy_cnt = 0
            total_cnt = self.each_coin_total_sell_cnt.get(coin_name.lower(), 0)
            self.each_coin_total_sell_cnt[coin_name.lower()] = total_cnt + 1
            
        self.save_state(exchange_name, coin_name, market, 'buy', buy_cnt, price, self.trading_cnt, accumulate_profit)
        
        ver = order['ver']
        __type = order['type']
        rule = order['rule']
        tsb1 = order['tsb-minute']
        tsb_ver = order['tsb-ver']
        order['price'] = price
        
        #나중에 Q를 사용하여 메시지를 전달할 땐 order 구조체를 json 타입으로 전달한다
        #build message for other TSB Slave bot
        message = f'#AUTO:0 #VER:{ver} #EXCHANGE:{exchange_name} #SIDE:{command} #TYPE:{__type} #COIN:{coin_name} #MARKET:{market} #PRICE:{price} #AMOUNT:100% #RULE:{rule} #TSB-MINUTE:{tsb1} #TSB-VER:{tsb_ver}\n'
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
        record_market['buy_total_cnt'] = self.each_coin_total_buy_cnt.get(coin, 0)   #해당코인의 총 구매회수
        record_market['sell_total_cnt'] = self.each_coin_total_sell_cnt.get(coin, 0)
        
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
        try:
            coin_list = Enviroments().strategies[class_name][exchange_name]
        except Exception as exp:
            self.logger.warning('strategies storage not exist : {}'.format(exp))
            coin_list = []
        
        #거래한 모든 코인의 수익율을 보여준다
        
        got_coin_list = []
        total_acc = 0
        buy_total_acc = 0
        trading_cnt = 0
        message = '매시간 보고서 \n'
        
        exchange = self.get_exchange(exchange_name)
        if(exchange is None):
            msg = '{} 이름이 유효하지 않습니다.'.format(exchange_name)
            self.logger.debug(msg)
            return False, msg
        
        for coin in coin_list:
            if(coin == 'trading_cnt'):
                trading_cnt = coin_list.get(coin)
                continue
            
            buy_info = coin_list.get(coin).get('krw')
            if(buy_info is None):
                continue
            
            acc = float(buy_info.get('accumulate', 0))
            total_buy = buy_info.get('buy_total_cnt', 0)
            total_sell = buy_info.get('sell_total_cnt', 0)
            message += '{:8} 구매 : {:4}  판매 : {:4} 수익 : {:6.2f}%\n'.format(coin.upper(), total_buy, total_sell, acc)
            total_acc += acc
        
        message += '봇거래한 누적 수익률 : {:.2f}%\n'.format(total_acc)
        
        ttime = datetime.now(pytz.timezone('Asia/Seoul')) 
        ttime = ttime.strftime('%Y-%m-%d %H:%M')
        
        message += '현재 시간(GMT+9) : {}'.format(ttime)
        
        return message
        
    def shedule_start(self):
        self.sched = BackgroundScheduler()
        self.sched.start()
        
        try:
            self.report_every_time()
            self.report_daily_report()
        except Exception as exp:
            self.logger.warning('exception in to print report : {}'.format(exp))
        
        # self.sched.add_job(self.report_every_time, 'cron', second='00', id='test')
        self.sched.add_job(self.report_every_time, 'cron', minute='00', id='report_every_time')
        self.sched.add_job(self.cleanup_daily, 'cron', hour='00', minute='05', id='cleanup_daily')
    
    def shedule_stop(self):
        # self.sched.remove_job('test')
        self.sched.remove_job('report_every_time')
        self.sched.remove_job('cleanup_daily')
        self.sched.shutdown()
    
    def report_every_time(self):
        msg = self.get_bought_coin_list()
        self.logger.debug('report time : {}'.format(msg))
        self.messenger_q.send('{}'.format(msg))
        
    def cleanup_daily(self):
        exchange_name = 'upbit' #현재는 upbit만 있으므로~
        
        #일일 데이터에서 거래횟수나 코인별 누적 수익률은 리셋 한다
        self.report_daily_report()
        
        class_name = self.__class__.__name__.lower()
        try:
            coin_list = Enviroments().strategies[class_name][exchange_name]
        except Exception as exp:
            self.logger.warning('strategies storage not exist : {}'.format(exp))
            coin_list = []
        
        self.trading_cnt = 0
        coin_list['trading_cnt'] = 0
        
        for coin in coin_list:
            if(coin == 'trading_cnt'):
                trading_cnt = coin_list.get(coin)
                continue
            
            buy_info = coin_list.get(coin).get('krw')
            if(buy_info is None):
                continue
            
            buy_info['accumulate'] = buy_info.get('accumulate', 0)
            buy_info['buy_total_cnt'] = buy_info.get('buy_total_cnt', 0)
            buy_info['sell_total_cnt'] = buy_info.get('sell_total_cnt', 0)
                
        
        Enviroments().save_config()
        
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
        try:
            coin_list = Enviroments().strategies[class_name][exchange_name]
        except Exception as exp:
            self.logger.warning('strategies storage not exist : {}'.format(exp))
            coin_list = []
        
        trading_cnt = int(coin_list.get('trading_cnt', 0))
        
        got_coin_list = []
        total_acc = 0
        
        coin_msg = '하루 거래 보고서 : {이름} {판매} {구매} {수익률}\n'
        for coin in coin_list:
            if(coin == 'trading_cnt'):
                continue
            
            buy_info = coin_list.get(coin).get('krw')
            if(buy_info is not None):
                acc = float(buy_info.get('accumulate', 0))
                total_buy = buy_info.get('buy_total_cnt', 0)
                total_sell = buy_info.get('sell_total_cnt', 0)
                
            total_acc += acc
            coin_msg += '{} : {:4} {:4}    {:.2f}%\n'.format(coin.upper(), total_buy, total_sell, acc)
            
        
        #날짜는 그냥 쓰도록 한다. 시스템 시간은 UTC 기준인데 한국 시간은 -9시간 해야한다
        #보고서가 출력되는 시간은 매일밤 자정이다
        #UTC시간으로 날짜가 변경되기 전이다.
        #그러므로 날짜는 그냥 쓰도록 한다.
        now = datetime.now()
        nowDate = now.strftime('%Y-%m-%d')
        
        message = f'{nowDate}\n'
        message += '총 거래 횟수 : {}\n'.format(trading_cnt)
        message += '누적 거래 수익률 : {:.2f}%\n'.format(total_acc)
        message += coin_msg
        
        self.logger.debug('daily report :\n{}'.format(message))
        self.messenger_q.send('{}'.format(message))
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
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    
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
    
    print('한번 구매 테스트')
    msg ='#AUTO:0 #COIN:NEO #MARKET:KRW #SIDE:BUY #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
        print('1 do buy : {}'.format(add_msg))
    
    msg ='#AUTO:0 #COIN:NEO #MARKET:KRW #SIDE:SELL #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
     print('1 do sell : {}'.format(add_msg))
    
    print('한번 구매 테스트')
    msg ='#AUTO:0 #COIN:IOTA #MARKET:KRW #SIDE:BUY #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
        print('1 do buy : {}'.format(add_msg))
    
    msg ='#AUTO:0 #COIN:IOTA #MARKET:KRW #SIDE:SELL #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
     print('1 do sell : {}'.format(add_msg))
    
    
    print('두번 구매 테스트')
    msg ='#AUTO:0 #COIN:BTC #MARKET:KRW #SIDE:BUY #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
        print('1 do buy : {}\n\n'.format(add_msg))
    
    msg ='#AUTO:0 #COIN:BTC #MARKET:KRW #SIDE:BUY #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
        print('2 do buy : {}\n\n'.format(add_msg))
    
    msg ='#AUTO:0 #COIN:BTC #MARKET:KRW #SIDE:SELL #TSB-MINUTE:45#TSB-VER:3.14#VER:1#RULE:TSB#EXCHANGE:UPBIT'
    do, add_msg = test.check_signal(msg)
    if(do):
        print('1 do sell : {}'.format(add_msg))
    
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
    
    
    # test.cleanup_daily()
    
    print(test.get_bought_coin_list())
    # test.report_daily_report()

    
    