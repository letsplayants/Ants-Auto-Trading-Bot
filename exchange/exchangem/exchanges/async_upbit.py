# -*- coding: utf-8 -*-
import logging
import time
import threading
import asyncio
import websockets
import json
import requests
import datetime

from exchangem.model.price_storage import PriceStorage

class ASyncUpbit():
    #ccxt에서 async를 열어서 데이터를 수신한 뒤 처리하는 로직 작성
    #ticker 데이터를 정기적으로 가지고 옴
    #가지고온 데이터는 60초간 캐싱
    #캐싱 데이터를 요청하면 캐싱 타임아웃 여부에 따라 데이터를 돌려줌
    def __init__(self):
        self.memory = {}
        self.recv_loop = True
        self.send_loop = True
        self.interval = 5       #5초마다 데이터를 갱신한다
        self.logger = logging.getLogger(__name__)
        self.price_storage = PriceStorage()
        self.websocket = None
        pass
    
    async def __run_recv__(self):
        #Ping-Pong 설정을 해야한다, 핑퐁 기본 구현되어있음. 업빗과 알아서 핑퐁 잘함
# 오더북 샘플
# KRW-BCH : {'ty': 'orderbook', 'cd': 'KRW-BCH', 'tms': 1560787779453, 'tas': 202.38848538, 'tbs': 147.1527989, 'obu': [{'ap': 511200.0, 'bp': 510900.0, 'as': 10.57098602, 'bs': 0.0237713}, {'ap': 511300.0, 'bp': 510800.0, 'as': 70.69436226, 'bs': 0.0408681}, {'ap': 511600.0, 'bp': 510700.0, 'as': 30.18680368, 'bs': 0.40376805}, {'ap': 512100.0, 'bp': 510600.0, 'as': 9.99, 'bs': 0.04256204}, {'ap': 512200.0, 'bp': 510500.0, 'as': 8.296, 'bs': 4.65755103}, {'ap': 512300.0, 'bp': 510400.0, 'as': 0.00244836, 'bs': 0.04522668}, {'ap': 512400.0, 'bp': 510300.0, 'as': 8.50558002, 'bs': 9.87250412}, {'ap': 512500.0, 'bp': 510200.0, 'as': 9.85325022, 'bs': 9.08949108}, {'ap': 512600.0, 'bp': 510100.0, 'as': 7.945, 'bs': 26.35366455}, {'ap': 512800.0, 'bp': 510000.0, 'as': 0.00244836, 'bs': 9.28122829}, {'ap': 512900.0, 'bp': 509900.0, 'as': 28.3054231, 'bs': 33.22748904}, {'ap': 513000.0, 'bp': 509700.0, 'as': 8.66954172, 'bs': 8.14937021}, {'ap': 513200.0, 'bp': 509600.0, 'as': 8.096, 'bs': 23.97105127}, {'ap': 513300.0, 'bp': 509500.0, 'as': 0.00244836, 'bs': 16.26567748}, {'ap': 513800.0, 'bp': 509400.0, 'as': 1.26819328, 'bs': 5.72857566}], 'st': 'REALTIME'}
# KRW-DCR : {'ty': 'orderbook', 'cd': 'KRW-DCR', 'tms': 1560787779453, 'tas': 43.59861893, 'tbs': 177.91705105, 'obu': [{'ap': 34210.0, 'bp': 33560.0, 'as': 2.97000297, 'bs': 2.7534}, {'ap': 34220.0, 'bp': 33550.0, 'as': 23.47774546, 'bs': 29.806}, {'ap': 34290.0, 'bp': 33320.0, 'as': 0.71729416, 'bs': 56.2}, {'ap': 34340.0, 'bp': 33220.0, 'as': 1.29550542, 'bs': 2.0}, {'ap': 34360.0, 'bp': 33200.0, 'as': 0.04737836, 'bs': 1.56659621}, {'ap': 34370.0, 'bp': 32990.0, 'as': 0.38450062, 'bs': 28.0}, {'ap': 34380.0, 'bp': 32880.0, 'as': 0.03301053, 'bs': 5.0}, {'ap': 34390.0, 'bp': 32730.0, 'as': 0.02323137, 'bs': 16.78714044}, {'ap': 34400.0, 'bp': 32690.0, 'as': 0.01828892, 'bs': 4.20404664}, {'ap': 34420.0, 'bp': 32650.0, 'as': 1.1, 'bs': 0.68290045}, {'ap': 34500.0, 'bp': 32560.0, 'as': 1.00906676, 'bs': 3.68550368}, {'ap': 34560.0, 'bp': 32520.0, 'as': 0.1, 'bs': 16.02704796}, {'ap': 34650.0, 'bp': 32400.0, 'as': 0.10092827, 'bs': 3.08641975}, {'ap': 34710.0, 'bp': 32340.0, 'as': 9.22166609, 'bs': 7.80858998}, {'ap': 34750.0, 'bp': 32320.0, 'as': 3.1, 'bs': 0.30940594}], 'st': 'REALTIME'}
# 현재가 샘플
# KRW-BCH : {'ty': 'ticker', 'cd': 'KRW-BCH', 'op': 509100.0, 'hp': 524800.0, 'lp': 508100.0, 'tp': 510500.0, 'pcp': 509800.0, 'atp': 20833988691.30604, 'c': 'RISE', 'cp': 700.0, 'scp': 700.0, 'cr': 0.0013730875, 'scr': 0.0013730875, 'ab': 'BID', 'tv': 0.14288839, 'atv': 40406.4139489, 'tdt': '20190617', 'ttm': '161317', 'ttms': 1560787997000, 'aav': 23652.72329474, 'abv': 16753.69065416, 'h52wp': 1040000.0, 'h52wdt': '2018-06-19', 'l52wp': 83620.0, 'l52wdt': '2018-12-15', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560787997948, 'atp24h': 24638571107.618538, 'atv24h': 47844.02311627, 'st': 'REALTIME'}
# KRW-XRP : {'ty': 'ticker', 'cd': 'KRW-XRP', 'op': 511.0, 'hp': 520.0, 'lp': 509.0, 'tp': 511.0, 'pcp': 511.0, 'atp': 37875194786.84065, 'c': 'EVEN', 'cp': 0.0, 'scp': 0.0, 'cr': 0, 'scr': 0, 'ab': 'ASK', 'tv': 3030.0, 'atv': 73750770.48785424, 'tdt': '20190617', 'ttm': '161317', 'ttms': 1560787997000, 'aav': 37080876.57326398, 'abv': 36669893.91459026, 'h52wp': 885.0, 'h52wdt': '2018-09-21', 'l52wp': 292.0, 'l52wdt': '2018-09-12', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560787997960, 'atp24h': 73938416795.68704, 'atv24h': 143913323.17611742, 'st': 'REALTIME'}
        async with websockets.connect(
                'wss://api.upbit.com/websocket/v1') as websocket:
            self.logger.info("connected")
            self.websocket = websocket
            
            # Snapshot mode로 send 요청을 날릴 땐 아래 주석을 풀어서 날린다.
            # self.send_thread_hnd = threading.Thread(target=self._run_send, args=())
            # self.send_thread_hnd.start()
            
            while self.recv_loop:
                cnt = 0
                message = await self.websocket.recv();
                self.consumer(message)
                cnt = cnt + 1
    
    def consumer(self, message):
        data = json.loads(message)
        
        
        self.logger.debug("%s : %s" % (data.get('cd'), data))
# KRW-TT : {'ty': 'ticker', 'cd': 'KRW-TT', 'op': 23.7, 'hp': 24.1, 'lp': 23.1, 'tp': 23.3, 'pcp': 23.7, 'atp': 909465642.869787, 'c': 'FALL', 'cp': 0.4, 'scp': -0.4, 'cr': 0.0168776371, 'scr': -0.0168776371, 'ab': 'ASK', 'tv': 11219.34033412, 'atv': 38776896.77642389, 'tdt': '20190618', 'ttm': '085100', 'ttms': 1560847860000, 'aav': 24791470.33970973, 'abv': 13985426.43671416, 'h52wp': 53.0, 'h52wdt': '2019-05-09', 'l52wp': 16.0, 'l52wdt': '2019-05-09', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560847860760, 'atp24h': 1495933525.146969, 'atv24h': 63739833.56441668, 'st': 'SNAPSHOT'}
# KRW-CRE : {'ty': 'ticker', 'cd': 'KRW-CRE', 'op': 49.8, 'hp': 50.4, 'lp': 46.5, 'tp': 47.2, 'pcp': 49.7, 'atp': 13282772489.233198, 'c': 'FALL', 'cp': 2.5, 'scp': -2.5, 'cr': 0.0503018109, 'scr': -0.0503018109, 'ab': 'BID', 'tv': 2010.91101694, 'atv': 279146350.58332807, 'tdt': '20190618', 'ttm': '085204', 'ttms': 1560847924000, 'aav': 176595353.4930699, 'abv': 102550997.0902582, 'h52wp': 122.0, 'h52wdt': '2019-05-17', 'l52wp': 5.14, 'l52wdt': '2019-05-17', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560847924202, 'atp24h': 49074141115.41804, 'atv24h': 1006959937.7375191, 'st': 'SNAPSHOT'}
# KRW-SOLVE : {'ty': 'ticker', 'cd': 'KRW-SOLVE', 'op': 455.0, 'hp': 456.0, 'lp': 439.0, 'tp': 441.0, 'pcp': 455.0, 'atp': 1370229811.7394612, 'c': 'FALL', 'cp': 14.0, 'scp': -14.0, 'cr': 0.0307692308, 'scr': -0.0307692308, 'ab': 'ASK', 'tv': 387.37842771, 'atv': 3088085.98083072, 'tdt': '20190618', 'ttm': '085134', 'ttms': 1560847894000, 'aav': 2287490.91903068, 'abv': 800595.06180004, 'h52wp': 853.0, 'h52wdt': '2019-06-05', 'l52wp': 424.0, 'l52wdt': '2019-06-09', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1560847894482, 'atp24h': 4391385944.401977, 'atv24h': 9703015.53051112, 'st': 'SNAPSHOT'}

# {'ty': 'trade', 'cd': 'KRW-BTC', 'tms': 1560864068071, 'td': '2019-06-18', 'ttm': '13:21:07', 'ttms': 1560864067000, 'tp': 10957000.0, 'tv': 3.8e-05, 'ab': 'BID', 'pcp': 11055000.0, 'c': 'FALL', 'cp': 98000.0, 'sid': 1560864067000000, 'st': 'SNAPSHOT'}
        
        coin_name = data.get('cd').split('-')[1]
        market_name = data.get('cd').split('-')[0]
        price = data.get('tp')
        timestamp = data.get('ttms')
        
        self.price_storage.set_price('UPBIT', market_name, coin_name, price, timestamp)

    def _run_recv(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__run_recv__())
        loop.close()

    def run(self):
        self.recv_thread_hnd = threading.Thread(target=self._run_recv, args=())
        self.recv_thread_hnd.start()
        
        krw = self.get_market_list()
        self.list_update(krw[0])
        
    
    def stop(self):
        self.recv_loop = False
        self.send_loop = False
        self.recv_thread_hnd.join()
        self.send_thread_hnd.join()
    
    
    def list_update(self, coins):
        self.target_coin = coins
        self._run_send()
        
    def _run_send(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._send())
        loop.close()
        
    async def _send(self):
# 현재가 -> ticker
# 체결 -> trade,
# 호가 ->orderbook
# isOnlyRealtime, isOnlySnapshot
        
        data=[
            {"ticket":"gob"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
            # {"type":'ticker',"codes":self.target_coin, "isOnlySnapshot":True},
            # {"type":'orderbook',"codes":self.target_coin, "isOnlySnapshot":True},
            {"type":'trade',"codes":self.target_coin, "isOnlyRealtime":True},
            {"format":"SIMPLE"}
        ]
            
        while self.websocket == None:
            self.logger.info('Wait for websocket connected.')
            time.sleep(1)
        
        await self.websocket.send(json.dumps(data))

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
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    upbit = ASyncUpbit()

    # coins = ['BTC', 'XRP', 'BCH', 'ETH', 'ETC', 'LTC', 'ADA', 'TRX', 'ZEC', 'DASH', 'OMG', 'XMR', 'DCR', 'SC', 'ZRX', 'BAT']
    coins = ['KRW-MEDX']

    import datetime
    import dateutil
    
    upbit.run()
    
    krw = upbit.get_market_list()
    print("call send")
    upbit.list_update(krw[0])
    print("calling send")
    
    max = -9999
    ps = PriceStorage()
    while(True):
        p = ps.get_price('UPBIT', 'KRW', 'ETH')
        if(p is None):
            print(f'p is none : {p}')
            
        if(p is not None):
            timestamp = p['timestamp']
            ttimestamp = datetime.datetime.fromtimestamp(timestamp/1000)
            now_time = datetime.datetime.now()
            st = now_time - ttimestamp
            print('KRW-BTC : {:,.2f}\ttime:{:.2f}\tmax gap : {:.2f}'.format(p['price'], st.total_seconds(), max))
            if(max < st.total_seconds()):
                max = st.total_seconds()
        time.sleep(5)
    
    # time.sleep(10)
    # coins = ['XRP']
    # upbit.list_update(coins)
    
    # time.sleep(10)
    # coins = ['ETH']
    # upbit.list_update(coins)