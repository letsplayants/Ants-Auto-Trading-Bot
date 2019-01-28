from bithumbpy.client import *

bithumb = Bithumb("", "")

# order 들어간거는 list 로 유지하던지 db 에 유지하던지...
# 일단 list 로 작업
# orderList = []

def get_orderbook(currency):
    result = bithumb.get_orderbook(currency, 10)

    if result is None:
        return None

    timestamp = int( result['timestamp'] )
    newOrderBook = []

    for i in range(9, -1, -1):
        # print( i, result['asks'][i], ' orderType:SELL' )
        newOrderBook.append({'price': float(result['asks'][i]['price']), 'size': float(result['asks'][i]['quantity']),
                             'orderType': 'SELL'})

    for i in range(0, 10):
        # print( i, result['bids'][i], ' orderType:BUY' )
        newOrderBook.append({'price': float(result['bids'][i]['price']), 'size': float(result['bids'][i]['quantity']),
                             'orderType': 'BUY'})

    newOrderBook = sorted(newOrderBook, key=lambda k: k['price'], reverse=True)

    i = -1
    for order in newOrderBook:
        i = i + 1
        # print( i, order)
        newOrderBook[i]['index'] = i
        # if i < 10:
        #     newOrderBook[i]['orderType'] = 'SELL'
        # else:
        #     newOrderBook[i]['orderType'] = 'BUY'

    if len(newOrderBook) != 20:
        return None

    response = {'timestamp': timestamp, 'orderbook': newOrderBook}

    return response

    # return newOrderBook


def get_balance(currency):
    result = bithumb.get_balance(currency)

    response = {"EXCHANGE": "BITHUMB", "KRW": 0, "COIN": 0}
    if result is not None:
        response = {"EXCHANGE":"BITHUMB", "KRW": result[4], "COIN": result[5]}
    #     response = {"EXCHANGE":"BITHUMB", "KRW": 0, "COIN": 0}
    # else:

    return response

def get_full_balance(currency):
    result = bithumb.get_full_balance()

    response = {"EXCHANGE": "BITHUMB", "KRW": 0, "COIN": 0}
    if result is not None:
        response = {"EXCHANGE":"BITHUMB", "result": result}
    #     response = {"EXCHANGE":"BITHUMB", "KRW": 0, "COIN": 0}
    # else:

    return response


def order(orderType, currency, price, size):
    result = None
    if orderType == "BUY":
        result = bithumb.buy_limit_order(currency, price, size)
    elif orderType == "SELL":
        result = bithumb.sell_limit_order(currency, price, size)

    global lastBithumbOrder
    lastBithumbOrder = result
    # orderList.append( result )
    return result

def get_lastorder():
    # order = search_order( order_id )
    global lastBithumbOrder
    result = bithumb.get_outstanding_order(lastBithumbOrder[0], lastBithumbOrder[1], lastBithumbOrder[2])
    return result


def cancel_lastorder():
    # order = search_order( order_id )
    global lastBithumbOrder
    result = bithumb.cancel_order(lastBithumbOrder[0], lastBithumbOrder[1], lastBithumbOrder[2])
    # result = bithumb.cancel_order(orderType, currency, order_id)
    if result is not None:
        lastBithumbOrder = None
        # orderList.remove( order )

    return result


# def search_order(order_id):
#     finedOrder = None
#     for order in orderList:
#         if order[2] == order_id:
#             finedOrder = order
#
#     return finedOrder

# def get_orders():
#     return orderList