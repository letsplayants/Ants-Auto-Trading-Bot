# -*- coding: utf-8 -*-
import dateutil.parser
import json

from env_server import Enviroments
from exchangem.exchanges.upbit import Upbit as cUpbit

#업빗에서는 거래 완료 시간이 생성되지 않는다.
#거래 생성된 시간만 기록이 되므로 이 시간을 기준으로 보고서를 작성한다
#거래 완료가 되었으면 거래 생성한 날의 거래가 완료된 것으로 간주한다

def get_trading_list(state, symbol=None, since=None, limit=None, uuids=None, page=1, params={}):
    upbit.exchange.load_markets()
    request = {
            # 'market': self.market_id(symbol),
            'state': state,
            'page': page,
            # 'uuids' : uuiids, uuid를 넣고 조회하면 invalid_query_payload 오류가 발생함 20190612
            'order_by': 'desc'
    }
    
    market = None
    if symbol is not None:
        market = self.exchange.market(symbol)
        request['market'] = market['id']
        
    return upbit.exchange.privateGetOrders(upbit.exchange.extend(request, params))

# https://datascienceschool.net/view-notebook/465066ac92ef4da3b0aba32f76d9750a/


def get_among_day(sday, eday, state='done', uuids=None):
    #state = ['done', 'cancel', 'wait']
    input = sday
    start_date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
    
    input = eday
    end_date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
    
    start_day = dateutil.parser.parse(start_date_string)
    end_day = dateutil.parser.parse(end_date_string)
    
    page = 0
    stop = False
    total = 0
    trading_cnt = 0
    total_bid = 0
    total_ask = 0
    trading_detail = {}
    report = {}
    coin_report = {}
    coin_report_list = {}
    while(not stop):
        page += 1
        
        order_list = get_trading_list(state, page=page)
        if(len(order_list) == 0):
            stop = True
        
        for item in order_list:
            # {'uuid': 'ab637e61-2899-4a3c-a71b-9fe09f6d88ec', 'side': 'bid', 'ord_type': 'limit', 'price': '1730.0', 'state': 'done', 'market': 'KRW-ONT', 'created_at': '2019-06-12T00:47:45+09:00', 'volume': '231.0982659', 'remaining_volume': '0.0', 'reserved_fee': '199.9000000035', 'remaining_fee': '0.0', 'paid_fee': '199.9000000035', 'locked': '0.0', 'executed_volume': '231.0982659', 'trades_count': 2}
            tarding_day = dateutil.parser.parse(item['created_at'])
            gap_start = start_day.date() - tarding_day.date()
            gap_end = end_day.date() - tarding_day.date()
            
            # sday = '20190605'
            # eday = '20190606'

            # 0 보다 작으면 지정된 날짜보다 이전이고
            # 0 보다 크면 지정된 날자보다 이후이다
            # 
            # end보다 날짜가 크면 계산안하고
            # start보다 날짜가 작으면 누적한다
            
                
            if(gap_end.days < 0):
                #지정된 날짜보다 이후 날짜면 다 통과
                # print("end : {} : {}, {} ".format(trading_cnt, item['created_at'], item['side']))
                continue
            
            if(gap_start.days > 0):
                print("end : {} : {}, {} ".format(trading_cnt, item['created_at'], item['side']))
                stop = True
                break
                
            # print('s : {}, gap: {}'.format(item['created_at'], gap_end.days))
            
            #check uuid
            if(uuids is not None and item['uuid'] not in uuids):
                continue
            
            market = item['market']
            if(market.find('KRW') < 0):
                continue
            
            if(coin_report_list.get(market) is not None):
                coin_report = coin_report_list[market]
            else:
                coin_report = {}
            
            if(item['ord_type'] != 'limit'):
                continue
            
            price = float(item['price'])
            volume = float(item['executed_volume'])
            fee = float(item['paid_fee'])
            trading_cnt += 1
            
            if(item['side'] == 'bid'): #ask가 매도 bid가 매수
                bid_price = price * volume - fee
                total_bid += bid_price
                coin_report['bid_cnt'] = coin_report['bid_cnt'] + volume if(coin_report.get('bid_cnt') is not None) else volume
                coin_report['bid_price'] = coin_report['bid_price'] + bid_price if(coin_report.get('bid_price') is not None) else bid_price
            else:
                ask_price = price * volume - fee
                total_ask += ask_price
                coin_report['ask_cnt'] = coin_report['ask_cnt'] + volume if(coin_report.get('ask_cnt') is not None) else volume
                coin_report['ask_price'] = coin_report['ask_price'] + ask_price if(coin_report.get('ask_price') is not None) else ask_price
                
            coin_report_list[market] = coin_report
            """
            {
               누적 수익 : 000%,
               코인별 수익 : {
                   'BTC' : {
                        'bid횟수': 10,
                        'bid_price' : 1000,
                        'ask_cnt' : 10,
                        'ask_pice' : 9000,
                        '수익' : 0%
                   }
                   ....
               }
            }
            """
            # print("{} : {}, {}, {}".format(trading_cnt, item['created_at'], item['side'], (price * volume - fee)))
    
    report = {
        'total' : total,
        'coin' : coin_report_list
    }
    total = total_ask - total_bid
    print(f'총 매수 금액 : {total_bid:,.2f} 총 매도 금액 : {total_ask:,.2f}')
    print('거래 횟수 : {}\n손익 : {:,.2f}'.format(trading_cnt, total))
    return report
    
    
def get_day_report(date_string, uuids=None):
    # input = sday
    # date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
    # print(date_string)
    target_day = dateutil.parser.parse(date_string)
    # target_day = dateutil.parser.parse('2019-06-04T00:00:00+09:00')
    page = 0
    stop = False
    total = 0
    trading_cnt = 0
    total_bid = 0
    total_ask = 0
    while(not stop):
        page += 1
        
        order_list = get_trading_list('done', page=page)
        
        for item in order_list:
            # 2019-06-08T09:14:27+09:00
            # print(item['created_at'])
            tarding_day = dateutil.parser.parse(item['created_at'])
            gap = target_day.date() - tarding_day.date()
            
            if(gap.days == 0):
                #원하는 날짜
                market = item['market']
                if(market.find('KRW') < 0):
                    continue
    
                if(item['ord_type'] != 'limit'):
                    continue
                
                #check uuid
                if(uuids is not None and item['uuid'] not in uuids):
                    continue
                
                price = float(item['price'])
                volume = float(item['volume'])
                fee = float(item['paid_fee'])
                trading_cnt += 1
                
                if(item['side'] == 'bid'): #ask가 매도 bid가 매수
                    total_bid += price * volume - fee
                else:
                    total_ask += price * volume - fee
                
                # print("{} : {}, {}, {}".format(trading_cnt, item['created_at'], item['side'], (price * volume - fee)))
                
                pass
            
            
            # if(gap.days < 0):
            #     #지정한 날짜보다 미래
            #     stop = True
            #     pass
            
            if(gap.days > 0):
                #지정된 날짜보다 과거
                print("Last : {} : {}, {}, {}".format(trading_cnt, item['created_at'], item['side'], (price * volume - fee)))
                stop = True
                break
        
    total = total_ask - total_bid
    print(f'총 매수 금액 : {total_bid:,.2f} 총 매도 금액 : {total_ask:,.2f}')
    print('거래 횟수 : {}\n손익 : {:,.2f}'.format(trading_cnt, total))


def bot_trading(want_date):
    # {'symbol': 'NEO/KRW', 'id': 'bba8aa34-1172-4e08-a985-e066cce7a78e', 'side': 'buy', 'price': 14890.0, 'amount': 26.85023506, 'status': 'open', 'remaining': 26.85023506, 'ts_create': 1560303915000, 'ts_updated': None}
    # {'symbol': 'EOS/KRW', 'id': 'c2f62565-0af9-4ee1-b905-162da2f469bc', 'side': 'sell', 'price': 7640.0, 'amount': 52.32984293, 'status': 'open', 'remaining': 52.32984293, 'ts_create': 1560304062000, 'ts_updated': None}

    data = []
    bot_order_list = []
    with open('logs/trading_record.1' , "r") as f:
        while(True):
            line = f.readline()
            
            if not line: break
            line = eval(line)
            data.append(line)
            bot_order_list.append(line['id'])
    
    print('bot 거래 결과 : ')
    get_day_report(want_date, bot_order_list)

def bot_trading_range(sdate, edate):
    # {'symbol': 'NEO/KRW', 'id': 'bba8aa34-1172-4e08-a985-e066cce7a78e', 'side': 'buy', 'price': 14890.0, 'amount': 26.85023506, 'status': 'open', 'remaining': 26.85023506, 'ts_create': 1560303915000, 'ts_updated': None}
    # {'symbol': 'EOS/KRW', 'id': 'c2f62565-0af9-4ee1-b905-162da2f469bc', 'side': 'sell', 'price': 7640.0, 'amount': 52.32984293, 'status': 'open', 'remaining': 52.32984293, 'ts_create': 1560304062000, 'ts_updated': None}

    data = []
    bot_order_list = []
    with open('logs/trading_record.1' , "r") as f:
        while(True):
            line = f.readline()
            
            if not line: break
            line = eval(line)
            data.append(line)
            bot_order_list.append(line['id'])
    
    
    trading_report = get_among_day(sdate, edate, uuids=bot_order_list)
    balance_report = upbit.get_all_balance()
    # print(balance_report)
    ticker = upbit.exchange.fetch_tickers()
    # print(ticker['BCH/KRW']['last'])
    # return
    
    # trading_report = {'total': 0, 'coin': {'KRW-LTC': {'bid_cnt': 14, 'bid_price': 3725671.821052077, 'ask_cnt': 13, 'ask_price': 3532644.317235578}, 'KRW-ONT': {'bid_cnt': 17, 'bid_price': 4456228.945982941, 'ask_cnt': 9, 'ask_price': 4162096.318517895}, 'KRW-XRP': {'bid_cnt': 11, 'bid_price': 2482302.9162260653, 'ask_cnt': 6, 'ask_price': 1584669.6523858113}, 'KRW-IOTA': {'bid_cnt': 15, 'bid_price': 4028907.744148271, 'ask_cnt': 9, 'ask_price': 3880292.236590186}, 'KRW-TRX': {'bid_cnt': 10, 'bid_price': 2514158.3257273254, 'ask_cnt': 8, 'ask_price': 2913919.542590617}, 'KRW-BSV': {'bid_cnt': 15, 'bid_price': 3996001.354014133, 'ask_cnt': 11, 'ask_price': 3891870.202425568}, 'KRW-BTC': {'bid_cnt': 8, 'bid_price': 2097900.62886804, 'ask_cnt': 7, 'ask_price': 1999676.2283766703}, 'KRW-EOS': {'bid_cnt': 15, 'bid_price': 3596917.171027454, 'ask_cnt': 12, 'ask_price': 3497136.853353749}, 'KRW-BCH': {'bid_cnt': 11, 'bid_price': 2351064.103643058, 'ask_cnt': 7, 'ask_price': 2157856.2807761747}, 'KRW-NEO': {'bid_cnt': 14, 'bid_price': 4137794.1903173113, 'ask_cnt': 10, 'ask_price': 3645024.8968317043}, 'KRW-ETC': {'ask_cnt': 10, 'ask_price': 3274446.9846633156, 'bid_cnt': 14, 'bid_price': 3370463.9185583233}, 'KRW-ETH': {'ask_cnt': 10, 'ask_price': 2920639.687866882, 'bid_cnt': 13, 'bid_price': 3009727.5740856593}, 'KRW-ATOM': {'ask_cnt': 10, 'ask_price': 4149550.451363871, 'bid_cnt': 14, 'bid_price': 3779158.7825058703}}}
    total_sum = 0
    print('bot 거래 결과 : ')
    for key in trading_report['coin']:
        item = trading_report['coin'][key]
        if(item is None or len(item) == 0):
            continue
        
        coin_name = key.split('-')[1]
        market = key.split('-')[0]
        symbol = coin_name + '/' + market
        
        ask_price = item['ask_price'] if item.get('ask_price') is not None else 0
        bid_price = item['bid_price'] if item.get('bid_price') is not None else 0
        bid_cnt = item['bid_cnt'] if item.get('bid_cnt') is not None else 0
        ask_cnt = item['ask_cnt'] if item.get('ask_cnt') is not None else 0
        balance = float(ticker[symbol]['last']) * float(bid_cnt - ask_cnt) if (bid_cnt - ask_cnt > 0) else 0
        
        sum = (ask_price + balance) - bid_price
        msg = key + '\n'
        msg += '예상 이익 : {:,.2f}\n'.format(sum)
        msg += '잔고 금액 : {:,.2f}\n'.format(balance)
        msg += '구매 금액 : {:,.2f}\n판매 금액 : {:,.2f}\n'.format(bid_price, ask_price)
        msg += '구매 개수 : {:.8f}\n판매 개수 : {:.8f}\n'.format(bid_cnt, ask_cnt)
        
        total_sum += sum
        
        print(msg)
    print('봇에 의한 거래 결과 : {:,.2f}'.format(total_sum))
        # print(trading_report)
    #트레이딩 결과에 보유분을 함께 표시해준다
    

env = Enviroments()
env.load_config()
upbit = cUpbit()

input = '20190612'
date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
target_day1 = dateutil.parser.parse(date_string)
# bot_trading(date_string)
# get_day_report(date_string)

# print(target_day1.date())

# input = '20190609'
# date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
# target_day2 = dateutil.parser.parse(date_string)

# t = target_day2.date() - target_day1.date()
# print(t)

# print(is_same_date(target_day, target_day))
# print(date_string)

sday = '20190614'
eday = '20190614'
# get_among_day(sday, eday)
bot_trading_range(sday, eday)


