# -*- coding: utf-8 -*-
import logging
import time
import threading
import asyncio
import websockets
import json
import requests

class ASyncUpbit():
    #ccxt에서 async를 열어서 데이터를 수신한 뒤 처리하는 로직 작성
    #ticker 데이터를 정기적으로 가지고 옴
    #가지고온 데이터는 60초간 캐싱
    #캐싱 데이터를 요청하면 캐싱 타임아웃 여부에 따라 데이터를 돌려줌
    def __init__(self):
        self.memory = {}
        self.expires_sec = 60   #기본은 60초간 캐싱한다
        self.logger = logging.getLogger(__name__)
        pass
    
    async def getOrderBook(self, coins):
        #Ping-Pong 설정을 해야한다, 핑퐁 기본 구현되어있음. 업빗과 알아서 핑퐁 잘함
# 오더북 샘플
# KRW-BCH : {'ty': 'orderbook', 'cd': 'KRW-BCH', 'tms': 1560787779453, 'tas': 202.38848538, 'tbs': 147.1527989, 'obu': [{'ap': 511200.0, 'bp': 510900.0, 'as': 10.57098602, 'bs': 0.0237713}, {'ap': 511300.0, 'bp': 510800.0, 'as': 70.69436226, 'bs': 0.0408681}, {'ap': 511600.0, 'bp': 510700.0, 'as': 30.18680368, 'bs': 0.40376805}, {'ap': 512100.0, 'bp': 510600.0, 'as': 9.99, 'bs': 0.04256204}, {'ap': 512200.0, 'bp': 510500.0, 'as': 8.296, 'bs': 4.65755103}, {'ap': 512300.0, 'bp': 510400.0, 'as': 0.00244836, 'bs': 0.04522668}, {'ap': 512400.0, 'bp': 510300.0, 'as': 8.50558002, 'bs': 9.87250412}, {'ap': 512500.0, 'bp': 510200.0, 'as': 9.85325022, 'bs': 9.08949108}, {'ap': 512600.0, 'bp': 510100.0, 'as': 7.945, 'bs': 26.35366455}, {'ap': 512800.0, 'bp': 510000.0, 'as': 0.00244836, 'bs': 9.28122829}, {'ap': 512900.0, 'bp': 509900.0, 'as': 28.3054231, 'bs': 33.22748904}, {'ap': 513000.0, 'bp': 509700.0, 'as': 8.66954172, 'bs': 8.14937021}, {'ap': 513200.0, 'bp': 509600.0, 'as': 8.096, 'bs': 23.97105127}, {'ap': 513300.0, 'bp': 509500.0, 'as': 0.00244836, 'bs': 16.26567748}, {'ap': 513800.0, 'bp': 509400.0, 'as': 1.26819328, 'bs': 5.72857566}], 'st': 'REALTIME'}
# KRW-DCR : {'ty': 'orderbook', 'cd': 'KRW-DCR', 'tms': 1560787779453, 'tas': 43.59861893, 'tbs': 177.91705105, 'obu': [{'ap': 34210.0, 'bp': 33560.0, 'as': 2.97000297, 'bs': 2.7534}, {'ap': 34220.0, 'bp': 33550.0, 'as': 23.47774546, 'bs': 29.806}, {'ap': 34290.0, 'bp': 33320.0, 'as': 0.71729416, 'bs': 56.2}, {'ap': 34340.0, 'bp': 33220.0, 'as': 1.29550542, 'bs': 2.0}, {'ap': 34360.0, 'bp': 33200.0, 'as': 0.04737836, 'bs': 1.56659621}, {'ap': 34370.0, 'bp': 32990.0, 'as': 0.38450062, 'bs': 28.0}, {'ap': 34380.0, 'bp': 32880.0, 'as': 0.03301053, 'bs': 5.0}, {'ap': 34390.0, 'bp': 32730.0, 'as': 0.02323137, 'bs': 16.78714044}, {'ap': 34400.0, 'bp': 32690.0, 'as': 0.01828892, 'bs': 4.20404664}, {'ap': 34420.0, 'bp': 32650.0, 'as': 1.1, 'bs': 0.68290045}, {'ap': 34500.0, 'bp': 32560.0, 'as': 1.00906676, 'bs': 3.68550368}, {'ap': 34560.0, 'bp': 32520.0, 'as': 0.1, 'bs': 16.02704796}, {'ap': 34650.0, 'bp': 32400.0, 'as': 0.10092827, 'bs': 3.08641975}, {'ap': 34710.0, 'bp': 32340.0, 'as': 9.22166609, 'bs': 7.80858998}, {'ap': 34750.0, 'bp': 32320.0, 'as': 3.1, 'bs': 0.30940594}], 'st': 'REALTIME'}
# 현재가 샘플
# KRW-BCH : {'ty': 'ticker', 'cd': 'KRW-BCH', 'op': 509100.0, 'hp': 524800.0, 'lp': 508100.0, 'tp': 510500.0, 'pcp': 509800.0, 'atp': 20833988691.30604, 'c': 'RISE', 'cp': 700.0, 'scp': 700.0, 'cr': 0.0013730875, 'scr': 0.0013730875, 'ab': 'BID', 'tv': 0.14288839, 'atv': 40406.4139489, 'tdt': '20190617', 'ttm': '161317', 'ttms': 1560787997000, 'aav': 23652.72329474, 'abv': 16753.69065416, 'h52wp': 1040000.0, 'h52wdt': '2018-06-19', 'l52wp': 83620.0, 'l52wdt': '2018-12-15', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560787997948, 'atp24h': 24638571107.618538, 'atv24h': 47844.02311627, 'st': 'REALTIME'}
# KRW-XRP : {'ty': 'ticker', 'cd': 'KRW-XRP', 'op': 511.0, 'hp': 520.0, 'lp': 509.0, 'tp': 511.0, 'pcp': 511.0, 'atp': 37875194786.84065, 'c': 'EVEN', 'cp': 0.0, 'scp': 0.0, 'cr': 0, 'scr': 0, 'ab': 'ASK', 'tv': 3030.0, 'atv': 73750770.48785424, 'tdt': '20190617', 'ttm': '161317', 'ttms': 1560787997000, 'aav': 37080876.57326398, 'abv': 36669893.91459026, 'h52wp': 885.0, 'h52wdt': '2018-09-21', 'l52wp': 292.0, 'l52wdt': '2018-09-12', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560787997960, 'atp24h': 73938416795.68704, 'atv24h': 143913323.17611742, 'st': 'REALTIME'}
        async with websockets.connect(
                'wss://api.upbit.com/websocket/v1') as self.websocket:
            self.logger.info("connected")
            
            #add prefix - KRW, USDT
            fixedCoins=[]
            for wd in coins:
                fixedCoins.append('KRW-' + wd)
                # fixedCoins.append('USDT-' + wd)
            
#             (현재가 -> ticker
# 체결 -> trade,
# 호가 ->orderbook)
            data=[
                {"ticket":"gob"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
                {"type":'ticker',"codes":fixedCoins, "isOnlySnapshot":True},
                {"type":'orderbook',"codes":fixedCoins, "isOnlySnapshot":True},
                {"type":'trade',"codes":fixedCoins, "isOnlySnapshot":True},
                {"format":"SIMPLE"}
                ]
            
            # await self.websocket.send(json.dumps(data))
            # self.logger.debug(f"> {data}")
    
            #감시 대상 코인 중 변경된 값이 있는 코인의 상태값을 돌려준다.
            # message = await websocket.recv()
            # self.logger.debug(f"< {message}")
            while True:
                cnt = 0
                message = await self.websocket.recv();
                self.consumer(message)
                cnt = cnt + 1
    
    def consumer(self, message):
        data = json.loads(message)
        # processPremium(data)
        # storage.setData(data.get('cd'), data)
        print("%s : %s" % (data.get('cd'), data))
        #TODO 업데이트된 코인에 대해서 소수점 4자리까지 %로 업데이트 한다
        #process()

    def _run(self):
        # coins = ['BTC', 'XRP', 'BCH', 'ETH', 'ETC', 'LTC', 'ADA', 'TRX', 'ZEC', 'DASH', 'OMG', 'XMR', 'DCR', 'SC', 'ZRX', 'BAT']
        coins = ['BTC']
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        print('in loop : {}'.format(loop))
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.getOrderBook(coins))
        # await self.getOrderBook(coins)

    def run(self):
        self.thread_hnd = threading.Thread(target=self._run, args=())
        self.thread_hnd.start()
    
    async def _send(self, coins):
        fixedCoins=[]
        # for wd in coins:
        #     fixedCoins.append('KRW-' + wd)
            # fixedCoins.append('USDT-' + wd)
#             (현재가 -> ticker
# 체결 -> trade,
# 호가 ->orderbook)
        data=[
            {"ticket":"gob"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
            {"type":'ticker',"codes":coins, "isOnlySnapshot":True},
            {"type":'orderbook',"codes":coins, "isOnlySnapshot":True},
            {"type":'trade',"codes":coins, "isOnlySnapshot":True},
            {"format":"SIMPLE"}
            ]
        await self.websocket.send(json.dumps(data))
        
    def list_update(self, coins):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._send(coins))
        
        # loop = asyncio.get_event_loop()
        # # Blocking call which returns when the hello_world() coroutine is done
        # loop.run_until_complete(self._send(coins))
        loop.close()
    
    def get_market_list(self):
        url = "https://api.upbit.com/v1/market/all"
        response = requests.request("GET", url)
        markets = eval(response.text)
        krw_market = []
        btc_market = []
        usdt_market = []
        for item in markets:
            m = item['market'].split('-')[0]
            if(m == 'KRW'):
                krw_market.append(item['market'])
                # print(item)
            elif(m == 'BTC'):
                btc_market.append(item['market'])
            elif(m == 'USDT'):
                usdt_market.append(item['market'])
        
        return krw_market, btc_market, usdt_market
        
if __name__ == '__main__':
    print('Cache module test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    upbit = ASyncUpbit()
    krw = upbit.get_market_list()
    
    print(krw[0])
    import time
    time.sleep(5)
    
    # coins = ['BTC', 'XRP', 'BCH', 'ETH', 'ETC', 'LTC', 'ADA', 'TRX', 'ZEC', 'DASH', 'OMG', 'XMR', 'DCR', 'SC', 'ZRX', 'BAT']
    # coins = ['BTC','XRP', 'BCH', 'ETH']

    upbit.run()
    time.sleep(10)
    upbit.list_update(krw[0])
    
    # time.sleep(10)
    # coins = ['XRP']
    # upbit.list_update(coins)
    
    # time.sleep(10)
    # coins = ['ETH']
    # upbit.list_update(coins)