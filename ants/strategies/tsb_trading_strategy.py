# -*- coding: utf-8 -*-
import logging

import traceback
import pytz
import threading
import sched, time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

import ants.strategies.strategy

from ants.provider.observers import Observer
from ants.provider.rabbitmq_rcv import MQProvider
from ants.performer.smart_trader import SmartTrader

from messenger.q_publisher import MQPublisher
from env_server import Enviroments
from exchangem.exchanges.upbit import Upbit as cUpbit
from candlebar_tracker import CandleBarTracker

class TSBTradingStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    TSB 포멧에 맞는 메시지가 들어오면 거기에 맞는 전략으로 거래를 수행한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.telegram_messenger_q_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.messenger_q = MQPublisher(self.telegram_messenger_q_name)
        self.logger.debug('telegram message q name : {}'.format(self.telegram_messenger_q_name))
    
        self.order_list = {}
        self.trader = SmartTrader()
        self.upbit = cUpbit()
        self.trader.add_exchange('UPBIT', self.upbit)
        
        self.__init_scheduler__()
        self.__init_sell_thread__()
    
    def __init_scheduler__(self):
        self.available_key_list = ['1m','5m','10m','15m','30m','45m','60m','120m','180m','240m','300m','360m','480m','720m','1440m']
        ct = CandleBarTracker()
        for key in self.available_key_list:
            minute = int(key[:len(key)-1])
            ct.add_event(minute, False, self.__batch_job__, minute) 
    
    def __init_sell_thread__(self):
        self.sell_thread_hnd = threading.Thread(target=self.__sell_run__, args=())
        self.sell_loop = True
        self.sell_interval = 60
        self.sell_list = {}
        self.sell_thread_hnd.start()
    
    def run(self):
        #전략에서 사용할 데이터 제공자를 등록 후 실행
        """
        {
            'tsb' : 'tsb.trading.botid'
        }
        """
        key = 'tsb'#rule name을 key로 가진다.
        if(Enviroments().qsystem.get(key) == None):
            value = 'tsb.trading.{}'.format(Enviroments().messenger['bot_id'])
            Enviroments().qsystem[key] = value
            Enviroments().save_config()
        
        self.data_provider = MQProvider(Enviroments().qsystem[key])
        self.data_provider.attach(self)
        self.data_provider.run()
        self.logger.info(f'{__name__} strategy run with {Enviroments().qsystem[key]}')

    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        #AUTO:0 #VER:1 #EXCHANGE:UPBIT #SIDE:BUY #TYPE:LIMIT #COIN:ONT #MARKET:KRW #PRICE:1585.0 #AMOUNT:100% #RULE:TSB #TSB-MINUTE:15 #TSB-VER:3.14
        ----------------------------------------------------------------------
        ONT/KRW
        1회차 구매 단가: 1,580.00
        2회차 구매 단가: 1,585.00
        평균 구매 단가: 1,582.50
        """
        self.logger.debug('got msg in data strategy : {}'.format(msg))
        
        #자동 매매용 메시지와 사람이 읽을 수 있는 문자 구분은 '-'*70 규칙으로 한다
        # split_key = '-'*70
        # msg=msg[:msg.find(split_key)]
        # msg = self.parsing(msg)
        # print(msg)
        self.do_action(msg)
    
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
            if(item.find('VER') > -1):
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
    
    def trading(self, msg):
        try:
            version = msg['ver']
            command = msg['side']
            exchange = msg['exchange']
            market = msg['market']
            coin_name = msg['coin']
            price = msg['price']
            amount = msg['amount']
            rule = msg['rule']
            etc = msg['etc']
        except Exception as exp:
            self.logger.warning('msg parsing error : {}'.format(exp))
            return
            
        symbol = coin_name + '/' + market
        self.logger.info('Try Action {} {}/{} {}'.format(exchange, coin_name, market, command))
        # try:
        #     availabel_size = self.trader.get_balance(exchange, coin_name, market, False)
        # except Exception as exp:
        #     self.logger.warning('Trading was failed : {}'.format(exp))
        #     return
        
        try:
            message, order_info = self.trader.trading(exchange, market, command, coin_name, price, amount, etc)
            #results는 ['msg']와 ['order_info']로 나눠져서 들어온다
            #order_info는 오더를 생성하고 서버에서 받은 정보를 가지고 있다. 즉 오더 id를 가지고 있음
            
            #생성된 오더 정보를 기반으로 추적 시스템에 넣는다
            #오더 분봉에 정보를 가지고 와서 분봉이 close되면 모든 오더가 취소되는 기능을 넣는다
            # message = result['msg']
            # order_info = result['order_info']
            self.logger.debug('trading result : \n{}\n{}'.format(message, order_info))
        except Exception as exp:
            self.messenger_q.send(str(exp))
            self.logger.warning('Trading was failed : {}'.format(exp))
            return
            
        if(order_info == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            self.messenger_q.send('실패 : 요청하신 내용을 실패하였습니다.\n{}'.format(order_info))
            return
        
        self.logger.info('Action Done {}'.format(order_info))
        self.messenger_q.send('요청하신 내용을 완료하였습니다.\n{}\n{}'.format(message, order_info))
        
        #캔들 트래킹
        minute = msg['tsb-minute']
        order_info['etc']['request'] = msg
        self.__set_watching_orders_by_minute__(minute, order_info)
    
    def __set_watching_orders_by_minute__(self, minute, order_info):
        minute = str(minute)
        self.logger.debug('add order to {}, {}'.format(minute, order_info))
        list = self.order_list.get(minute)
        if(list is None):
            list = []
        
        list.append(order_info)
        self.order_list[minute] = list
    
    def __get_watching_orders_by_minute__(self, minute):
        minute = str(minute)
        return self.order_list.get(minute)
    
    def __get_watching_order_by_uuid__(self, minute, uuid):
        minute = str(minute)
        self.logger.debug('get order to {}, {}'.format(minute, uuid))
        list = self.order_list.get(minute)
        if(list is None):
            return
        
        for item in self.order_list[minute]:
            if(item['id'] == uuid):
                return item
        
        return None
    
    def __del_watching_orders_by_uuid__(self, minute, uuid):
        minute = str(minute)
        self.logger.debug('del order to {}, {}'.format(minute, uuid))
        list = self.order_list.get(minute)
        if(list is None):
            return
        
        for item in self.order_list[minute]:
            if(item['id'] == uuid):
                self.order_list[minute].remove(item)
        
    def __batch_job__(self, minute):
        #지정된 시간에 맞는 모든 오더를 한번에 체크한다
        self.logger.debug('batch_job : {}'.format(minute))
        order_list = self.__get_watching_orders_by_minute__(minute)
        if(order_list is None):
            self.logger.debug('job is none')
            return
        
        order_id_list = {
            'UPBIT':[],
            'BITHUMB':[],
            'BINANCE':[]
            }
        for order in order_list:
            self.logger.debug(f'order : {order}')
            # order : {'symbol': 'BTC/KRW', 'id': 'bc4c4e36-2e10-4db8-98f6-c941b1e82287', 'side': 'buy', 'price': 6447000.0, 'amount': 0.01550333, 'status': 'open', 'remaining': 0.01550333, 'ts_create': 1563257248000, 'ts_updated': None, 'exchange': 'upbit', 'from_who': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}, 'etc': {'request': {'auto': '0', 'ver': '1', 'exchange': 'UPBIT', 'side': 'BUY', 'type': 'LIMIT', 'coin': 'BTC', 'market': 'KRW', 'price': '-50%', 'amount': '100%', 'rule': 'TSB', 'tsb-minute': '1', 'tsb-ver': '3.14', 'etc': {'from': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}}}}}
            exchange = order['etc']['request']['exchange']
            order_id_list[exchange].append(order['id'])
            
        self.logger.debug('order id list : {}'.format(order_id_list))
        
        # 대규모 오더 조회를 한 후
        # 거래소별로 주문조회
        for exchange_name in order_id_list:
            self.logger.debug(f'fetch order details from {exchange_name}')
            details = self.trader.fetch_orders_by_uuids(exchange_name, order_id_list[exchange_name])
            self.logger.debug('details : {}'.format(details))
            if(details is None):
                continue
            
            for item in details:
                # details : [{'uuid': 'b64de551-2fa6-4ff3-984e-6f4ea0863333', 'side': 'bid', 'ord_type': 'limit', 'price': '6417000.0', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2019-07-16T16:05:11+09:00', 'volume': '0.01557581', 'remaining_volume': '0.01557581', 'reserved_fee': '49.974986385', 'remaining_fee': '49.974986385', 'paid_fee': '0.0', 'locked': '99999.947756385', 'executed_volume': '0.0', 'trades_count': 0}]
                if(item['state'] == 'wait'): # 미완료일 경우
                    if(item['side'] == 'bid'): # BUY경우 취소
                        self.logger.debug('{} will cancel'.format(item))
                        ret = self.trader.cancel_order(exchange_name, item['uuid'])
                        #TODO 주문 실패할 경우 후속처리를 해야한다
                        self.logger.debug('cancel result : {}'.format(ret))
                    elif(item['side'] == 'ask'): # SELL일 땐 시장가 매도
                        self.logger.debug('reorder : {}'.format(item))
                        #현재 가격과 주문 가격을 비교 후 현재 가격이 주문 가격 보다 더 낮을 경우 관리 목록에 추가한다
                        request_order = self.__get_watching_order_by_uuid__(minute, item['uuid'])
                        
                        # 지속적으로 모니터링하면서 매도하도록 한다
                        self.add_to_fast_sell_list(request_order)
                        
                        self.logger.debug('reorder done'.format(item))
                    else:
                        self.logger.error('{}\nthis case can not process'.format(item))
                elif (item['state'] == 'done'):
                    self.logger.debug('{} was done'.format(item))
                elif (item['state'] == 'cancel'):
                    self.logger.debug('{} was cancel'.format(item))
                else :
                    self.logger.error('{}\nthis case can not process'.format(item))
                
                self.__del_watching_orders_by_uuid__(minute, item['uuid'])
                
        # self.logger.debug('order checking : {}'.format(detail))
        # order checking : {'symbol': 'BTC/KRW', 'id': '69be9aff-656f-4870-b1f0-f438fc2b29a7', 'side': 'buy', 'price': 6453000.0, 'amount': 0.01548892, 'status': 'open', 'remaining': 0.01548892, 'ts_create': 1563243639000, 'ts_updated': None, 'exchange': 'upbit', 'from_who': 'unknow', 'etc': {'request': {'auto': '0', 'ver': '1', 'exchange': 'UPBIT', 'side': 'BUY', 'type': 'LIMIT', 'coin': 'BTC', 'market': 'KRW', 'price': '-50%', 'amount': '100%', 'rule': 'TSB', 'tsb-minute': '1', 'tsb-ver': '3.14', 'etc': {'from': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}}}}}
        # detail['status'] == 'open', 'wait','done', 'cancel'
        pass
    
    def __sell_run__(self):
        while self.sell_loop:
            try:
            
                time.sleep(self.sell_interval)
                #지정된 시간에 맞는 모든 오더를 한번에 체크한다
                self.logger.debug('do sell_batch_job')
                order_list = self.sell_list
                if(order_list is None):
                    self.logger.debug('job is none')
                    continue
                
                order_id_list = {
                    'UPBIT':[],
                    'BITHUMB':[],
                    'BINANCE':[]
                    }
                for order_id in order_list:
                    order = order_list[order_id]
                    self.logger.debug(f'order : {order}')
                    # order : {'symbol': 'BTC/KRW', 'id': 'bc4c4e36-2e10-4db8-98f6-c941b1e82287', 'side': 'buy', 'price': 6447000.0, 'amount': 0.01550333, 'status': 'open', 'remaining': 0.01550333, 'ts_create': 1563257248000, 'ts_updated': None, 'exchange': 'upbit', 'from_who': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}, 'etc': {'request': {'auto': '0', 'ver': '1', 'exchange': 'UPBIT', 'side': 'BUY', 'type': 'LIMIT', 'coin': 'BTC', 'market': 'KRW', 'price': '-50%', 'amount': '100%', 'rule': 'TSB', 'tsb-minute': '1', 'tsb-ver': '3.14', 'etc': {'from': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}}}}}
                    exchange = order['etc']['request']['exchange'].upper()
                    order_id_list[exchange].append(order['id'])
                    
                self.logger.debug('sell order id list : {}'.format(order_id_list))
                
                # 대규모 오더 조회를 한 후
                # 거래소별로 주문조회
                for exchange_name in order_id_list:
                    self.logger.debug(f'fetch order details from {exchange_name}')
                    details = self.trader.fetch_orders_by_uuids(exchange_name, order_id_list[exchange_name])
                    self.logger.debug('details : {}'.format(details))
                    if(details is None):
                        continue
                    
                    for item in details:
                        # details : [{'uuid': 'b64de551-2fa6-4ff3-984e-6f4ea0863333', 'side': 'bid', 'ord_type': 'limit', 'price': '6417000.0', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2019-07-16T16:05:11+09:00', 'volume': '0.01557581', 'remaining_volume': '0.01557581', 'reserved_fee': '49.974986385', 'remaining_fee': '49.974986385', 'paid_fee': '0.0', 'locked': '99999.947756385', 'executed_volume': '0.0', 'trades_count': 0}]
                        if(item['state'] == 'wait'): # 미완료일 경우
                            if(item['side'] == 'ask'): # SELL일 땐 시장가 매도
                                self.logger.debug('reorder again : {}\nrequest : {}'.format(item, self.sell_list[item['uuid']]))
                                #현재 가격과 주문 가격을 비교 후 현재 가격이 주문 가격 보다 더 낮을 경우 기존 주문을 취소 후 재주문한다
                                request_order = self.sell_list[item['uuid']]
                                order_price = float(item['price'])
                                market = item['market'].split('-')[0]
                                coin = item['market'].split('-')[1]
                                action = 'buy' if item['side'] == 'bid' else 'sell'
                                now_price = self.trader.exchanges[exchange_name].get_last_price('{}/{}'.format(coin, market))
                                amount = '100%'
                                etc = request_order['etc']
                                
                                if(order_price > now_price):#기존 오더 가격이랑 현시세랑 비교한다
                                    # 기존 주문 취소 후 
                                    # 남은 물량이 얼만지 확인 후 남은 물량 만큼 재주문 한다
                                    remaining_volume = item['remaining_volume']
                                    amount = remaining_volume   #남은 수량
                                    
                                    ret = self.trader.cancel_order(exchange_name, item['uuid'])
                                    #TODO ret가 실패시 처리해야함
                                    
                                    # 주문 실패시 후속 처리 해야함
                                    # 취소된 물량이 바로 사용가능한 물량으로 집계되지 않는다.
                                    # 판매용 큐를 둬서 몇 판매를 따로 관리하도록 한다.
                                    # 임시로 약 2초간의 텀을 둔 후 판매를 하도록 한다. 2019-07-22
                                    # 약간의 시간 텀을 두고 판매를 시도한다
                                    # 시장가 매도
                                    time.sleep(5)
                                    message, order_info = self.trader.trading(exchange_name, market, action, coin, now_price, amount, etc)
                                    #order_info가 none일 경우 처리해야함
                                    if(order_info is None): #주문 실패 시 다음 기회를 노린다
                                        self.logger.warning(f'sell order retry after one minute cause : {message}')
                                        continue
                                        
                                    order_info['etc']['request'] = request_order
                                    del self.sell_list[item['uuid']]
                                    self.add_to_fast_sell_list(order_info)
                                        
                                    self.logger.debug('reorder : {}'.format(ret))
                            else:
                                self.logger.error('{}\nthis case can not process'.format(item))
                        elif (item['state'] == 'done'):
                            self.logger.debug('{} was done'.format(item))
                            del self.sell_list[item['uuid']]
                        elif (item['state'] == 'cancel'):
                            self.logger.debug('{} was cancel'.format(item))
                            del self.sell_list[item['uuid']]
                        else :
                            self.logger.error('{}\nthis case can not process'.format(item))
                        
                # self.logger.debug('order checking : {}'.format(detail))
                # order checking : {'symbol': 'BTC/KRW', 'id': '69be9aff-656f-4870-b1f0-f438fc2b29a7', 'side': 'buy', 'price': 6453000.0, 'amount': 0.01548892, 'status': 'open', 'remaining': 0.01548892, 'ts_create': 1563243639000, 'ts_updated': None, 'exchange': 'upbit', 'from_who': 'unknow', 'etc': {'request': {'auto': '0', 'ver': '1', 'exchange': 'UPBIT', 'side': 'BUY', 'type': 'LIMIT', 'coin': 'BTC', 'market': 'KRW', 'price': '-50%', 'amount': '100%', 'rule': 'TSB', 'tsb-minute': '1', 'tsb-ver': '3.14', 'etc': {'from': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}}}}}
                # detail['status'] == 'open', 'wait','done', 'cancel'
                pass
            except Exception as exp:
                err_str = traceback.format_exc()
                self.logger.error('Exception in sell_thread : \t{}\n{}'.format(exp, err_str))
            
    def add_to_fast_sell_list(self, order):
        self.sell_list[order['id']] = order
        
    def do_action(self, msg):
        """
        {'auto': '0', 'ver': '1', 'exchange': 'UPBIT', 'side': 'BUY', 'type': 'LIMIT', 'coin': 'ONT', 'market': 'KRW', 'price': '1585.0', 'amount': '100%', 'rule': 'TSB', 'tsb-minute': '15', 'tsb-ver': '3.14'}
        """
        try:
            version = msg['ver']
            side = msg['side']
        except Exception as exp:
            self.logger.warning('msg parsing error : {}'.format(exp))
            return
        
        if(side in ['BUY', 'SELL']):
            self.trading(msg)
        else:
            self.logger.warning('side parsing error : {}'.format(side))
            self.messenger_q.send('side가 잘못되었습니다 : {}\n원본:\n{}'.format(side,msg))
        
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
    logging.getLogger("websockets").setLevel(logging.ERROR)
    
    tsb_trading = TSBTradingStrategy()
    
    msg = {
        'auto': '0', 
        'ver': '1', 
        'exchange': 'UPBIT', 
        'side': 'BUY', 
        'type': 'LIMIT', 
        'coin': 'BTC', 
        'market': 'KRW', 
        'price': '100000.0', 
        'amount': '100%', 
        'rule': 'TSB', 
        'tsb-minute': '15', 
        'tsb-ver': '3.14',
        'etc':{
            'from' : 'test_code'
        }
    }
    
    tsb_trading.update(msg)
    
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
    
    
    # test.cleanup_daily()
    
    # print(test.get_bought_coin_list())
    # test.report_daily_report()

    
    