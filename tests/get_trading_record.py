# -*- coding: utf-8 -*-
import dateutil.parser

from env_server import Enviroments
from exchangem.exchanges.upbit import Upbit as cUpbit

env = Enviroments()
env.load_config()

upbit = cUpbit()

#업빗에서는 거래 완료 시간이 생성되지 않는다.
#거래 생성된 시간만 기록이 되므로 이 시간을 기준으로 보고서를 작성한다
#거래 완료가 되었으면 거래 생성한 날의 거래가 완료된 것으로 간주한다

def get_trading_list(state, symbol=None, since=None, limit=None, page=1, params={}):
    upbit.exchange.load_markets()
    request = {
            # 'market': self.market_id(symbol),
            'state': state,
            'page': page,
            'order_by': 'desc',
    }
    market = None
    if symbol is not None:
        market = self.exchange.market(symbol)
        request['market'] = market['id']
        
    return upbit.exchange.privateGetOrders(upbit.exchange.extend(request, params))


# https://datascienceschool.net/view-notebook/465066ac92ef4da3b0aba32f76d9750a/


def get_among_day(sday, eday):
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
    while(not stop):
        page += 1
        
        order_list = get_trading_list('done', page=page)
        if(len(order_list) == 0):
            stop = True
        
        for item in order_list:
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
            
            
            market = item['market']
            if(market.find('KRW') < 0):
                continue

            if(item['ord_type'] != 'limit'):
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
            
            # if(gap.days < 0):
            #     #지정한 날짜보다 미래
            #     stop = True
            #     pass
            
    total = total_ask - total_bid
    print(f'총 매수 금액 : {total_bid:,.2f} 총 매도 금액 : {total_ask:,.2f}')
    print('거래 횟수 : {}\n손익 : {:,.2f}'.format(trading_cnt, total))
    
    
def get_day_report(date_string):
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


def is_same_date(date1, date2):
    date1_year = date1.strftime('%Y')
    date1_month = date1.strftime('%m')
    date1_day = date1.strftime('%d')
    
    date2_year = date2.strftime('%Y')
    date2_month = date2.strftime('%m')
    date2_day = date2.strftime('%d')
    
    if(date1_year == date2_year and
        date1_month == date2_month and
        date1_day == date1_day):
            return True
    
    return False
    

input = '20190609'
date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
target_day1 = dateutil.parser.parse(date_string)

# print(target_day1.date())

# input = '20190609'
# date_string = '{}-{}-{}T00:00:00+09:00'.format(input[0:4], input[4:6], input[6:8])
# target_day2 = dateutil.parser.parse(date_string)

# t = target_day2.date() - target_day1.date()
# print(t)

# print(is_same_date(target_day, target_day))
# print(date_string)
# get_day_report(date_string)

sday = '20190609'
eday = '20190609'
get_among_day(sday, eday)

