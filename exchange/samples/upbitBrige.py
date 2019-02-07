from math import ceil, floor
from upbitpy.upbitpy import Upbitpy

upbit = Upbitpy("", "")

# orderList = []

def get_orderbook( currency ):
    result = upbit.get_orderbook(['KRW-' + currency])

    if result is None:
        return None

    timestamp = result[0]['timestamp']
    orderbook = result[0]['orderbook_units']
    # newOrderBook = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
    newOrderBook = []
    # print( orderbook[0] )
    for order in orderbook:
        newOrderBook.append({'price': order['ask_price'], 'size': order['ask_size']})
        newOrderBook.append({'price': order['bid_price'], 'size': order['bid_size']})

        # newOrderBook[9-i]['price'] = order['ask_price']
        # newOrderBook[9+i]['price'] = order['bid_price']

    # print( newOrderBook )

    newOrderBook = sorted(newOrderBook, key=lambda k: k['price'], reverse=True)

    i = -1
    for order in newOrderBook:
        i = i + 1
        # print( i, order)
        newOrderBook[i]['index'] = i
        if i < 10:
            newOrderBook[i]['orderType'] = 'SELL'
        else:
            newOrderBook[i]['orderType'] = 'BUY'


    if len(newOrderBook) != 20:
        return None
    # sorted(newOrderBook2.values(), key=lambda v: v['price'])
    response = {'timestamp' : timestamp, 'orderbook' : newOrderBook }

    return response


def get_balance( currency ):
    result = upbit.get_accounts()

    if result is None:
        return {"EXCHANGE":"UPBIT", "KRW": 0, "COIN": 0}

    currency_index = next((index for (index, d) in enumerate(result) if d["currency"] == currency.upper() ), None)
    krw_index = next((index for (index, d) in enumerate(result) if d["currency"] == 'KRW'), None)

    # print( currency_index )

    available_krw = 0
    available_currency = 0
    if( currency_index is not None and krw_index is not None ):
        # available_krw = float(result[krw_index]['balance']) - float(result[krw_index]['locked'])
        available_krw = float( result[krw_index]['balance'] )
        # available_krw = round( available_krw, 1)
        # available_currency = float(result[currency_index]['balance']) - float(result[currency_index]['locked'])
        # available_currency = round(available_currency, 7)
        available_currency = float(result[currency_index]['balance'])

    response = {"EXCHANGE":"UPBIT", "KRW": available_krw, "COIN": available_currency }
    # response = {"KRW": float(result["data"]["available_krw"]), "COIN": float(result["data"]["available_" + currency.lower()])}

    return response

def get_full_balance(currency):
    result = upbit.get_accounts()

    if result is None:
        return {"EXCHANGE": "UPBIT", "KRW": 0, "COIN": 0}
    #
    # currency_index = next((index for (index, d) in enumerate(result) if d["currency"] == currency.upper()), None)
    # krw_index = next((index for (index, d) in enumerate(result) if d["currency"] == 'KRW'), None)
    #
    # # print( currency_index )
    #
    # available_krw = 0
    # available_currency = 0
    # if (currency_index is not None and krw_index is not None):
    #     # available_krw = float(result[krw_index]['balance']) - float(result[krw_index]['locked'])
    #     available_krw = float(result[krw_index]['balance'])
    #     # available_krw = round( available_krw, 1)
    #     available_currency = float(result[currency_index]['balance']) - float(result[currency_index]['locked'])
    #     available_currency = round(available_currency, 7)

    response = {"EXCHANGE": "UPBIT", "result": result}
    # response = {"KRW": float(result["data"]["available_krw"]), "COIN": float(result["data"]["available_" + currency.lower()])}

    return response

    # if result["status"] == "0000":
    #     return {"KRW":float(result["data"]["available_krw"]),"COIN":float(result["data"]["available_"+coinType.lower()])}
    # else:
    #     return {"KRW":0,"COIN":0}


def order( orderType, currency, price, size ):
    result = None
    if orderType == "BUY":
        result = upbit.order('KRW-' + currency, 'bid', size, price)
    elif orderType == "SELL":
        result = upbit.order('KRW-' + currency, 'ask', size, price)

    global lastUpbitOrder
    lastUpbitOrder = result

    return result


def get_lastorder():
    global lastUpbitOrder
    result = upbit.get_order( lastUpbitOrder['uuid'] )
    return result


def cancel_lastorder():
    global lastUpbitOrder
    # order = search_order( order_id )
    result = upbit.cancel_order( lastUpbitOrder['uuid'] )

    if result is not None:
        lastUpbitOrder = None
        # orderList.remove( order )

    return result


# def search_order(order_id):
#     finedOrder = None
#     for order in orderList:
#         if order['uuid'] == order_id:
#             finedOrder = order
#
#     return finedOrder