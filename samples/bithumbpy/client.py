from termcolor import colored
from bithumbpy.core import *
import math

TAG = "BITHUMB"
class Bithumb:
    def __init__(self, conkey, seckey):
        self.api = PrivateApi(conkey, seckey)

    @staticmethod
    def _convert_unit(unit):
        try:
            unit = math.floor(unit * 10000) / 10000
            return unit
        except:
            return 0

    @staticmethod
    def get_tickers():
        """
        빗썸이 지원하는 암호화폐의 리스트
        :return:
        """
        try:
            resp = PublicApi.ticker("ALL")
            return list(resp['data'].keys())[:-1]
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_ohlc(currency):
        """
        최근 24시간 내 암호 화폐의 OHLC의 튜플
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : 코인과 (시가, 고가, 저가, 종가) 가 딕셔너리로 저장
          {
            'BTC' : (7020000.0, 7093000.0, 6810000.0, 6971000.0)
            'ETH' : ( 720000.0,  703000.0,  681000.0,  697000.0)
          }
        """
        try:
            resp = PublicApi.ticker(currency)['data']
            if currency is "ALL":
                del resp['date']
                data = {}
                for key in resp:
                        data[key] = (resp[key]['opening_price'], resp[key]['max_price'], resp[key]['min_price'], resp[key]['closing_price'])
                return data

            return {
                currency: (float(resp['opening_price']), float(resp['max_price']), float(resp['min_price']),
                           float(resp['closing_price']))
            }

        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_market_detail(currency):
        """
        거래소 마지막 거래 정보 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (24시간저가, 24시간고가, 24시간평균거래금액, 24시간거래량)
        """
        try:
            resp = None
            resp = PublicApi.ticker(currency)
            low = resp['data']['min_price']
            high = resp['data']['max_price']
            avg = resp['data']['average_price']
            volume = resp['data']['units_traded']
            return float(low), float(high), float(avg), float(volume)
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_current_price(currency):
        """
        최종 체결 가격 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : price
        """
        try:
            resp = PublicApi.ticker(currency)

            if currency is not "ALL":
                return float(resp['data']['closing_price'])
            else:
                return resp["data"]

        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_orderbook(currency, limit=5):
        """
        매수/매도 호가 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : 매수/매도 호가
        """
        try:
            resp = PublicApi.orderbook(currency, limit)
            return resp['data']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_trading_fee(self):
        """
        거래 수수료 조회
        :return: 수수료
        """
        try:
            resp = self.api.account()
            return float(resp['data']['trade_fee'])
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_balance(self, currency):
        """
        거래소 회원의 잔고 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (보유코인, 사용중코인, 보유원화, 사용중원화)
        """
        try:
            resp = self.api.balance(currency=currency)
            # print( resp )
            specifier = currency.lower()
            return (resp['data']["total_" + specifier], resp['data']["in_use_" + specifier],
                    resp['data']["total_krw"], resp['data']["in_use_krw"],
                    resp['data']["available_krw"], resp['data']["available_" + specifier])
            # return (float(resp['data']["total_" + specifier]), float(resp['data']["in_use_" + specifier]),
            #         float(resp['data']["total_krw"]), float(resp['data']["in_use_krw"]),
            #         float(resp['data']["available_krw"]), float(resp['data']["available_" + specifier]))
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_full_balance(self):
        """
        거래소 회원의 잔고 조회
        :param currency: ALL
        :return        : (보유코인, 사용중코인, 보유원화, 사용중원화)
        """
        currency = 'ALL'
        try:
            resp = self.api.balance(currency=currency)
            # print( resp )
            return resp
            # return (float(resp['data']["total_" + specifier]), float(resp['data']["in_use_" + specifier]),
            #         float(resp['data']["total_krw"]), float(resp['data']["in_use_krw"]),
            #         float(resp['data']["available_krw"]), float(resp['data']["available_" + specifier]))
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def buy_limit_order(self, currency, price, unit):
        """
        매수 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.place(type="bid", price=price, units=unit, order_currency=currency)
            return "bid", currency, resp['order_id']
        except Exception as x:
            print(resp)
            print(x.__class__.__name__, resp)
            return None

    def sell_limit_order(self, currency, price, unit):
        """
        매도 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.place(type="ask", price=price, units=unit, order_currency=currency)
            return "ask", currency, resp['order_id']
        except Exception as x:
            print(resp)
            print(x.__class__.__name__, resp)
            return None

    def get_outstanding_order(self, orderType, currency, order_id):
        """
        거래 미체결 수량 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래 미체결 수량
        """
        try:
            resp = self.api.orders(type=orderType, currency=currency, order_id=order_id)
            if resp['status'] == '5600':
                return None
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data'][0]['units_remaining']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_order_completed(self, orderType, currency, order_id):
        """
        거래 완료 정보 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래정보
        """
        try:
            resp = self.api.order_detail(type=orderType, currency=currency, order_id=order_id)
            if resp['status'] == '5600':
                return None
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data'][0]
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def cancel_order(self, orderType, currency, order_id):
        """
        매수/매도 주문 취소
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 성공: True / 실패: False
        """
        try:
            resp = self.api.cancel(type=orderType, currency=currency, order_id=order_id)
            return resp['status'] == '0000'
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def buy_market_order(self, currency, unit):
        """
        시장가 매수
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.market_buy(currency=currency, units=unit)
            return resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def sell_market_order(self, currency, unit):
        """
        시장가 매도
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.market_sell(currency=currency, units=unit)
            return resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None


if __name__ == "__main__":
    bithumb = Bithumb("2cd0b14eae8e6b214f4ab7f8274eab57", "9320ad8b5e363f7a960d4782e8b061f4")

    print(bithumb.get_tickers())
    print(bithumb.get_current_price("BTC"))

    time.sleep(5)

    desc = bithumb.buy_limit_order("BTC", 7100000, 1)
    print( desc )
    quanity = bithumb.get_outstanding_order(desc)
    print( quanity )

    time.sleep(10)
    status = bithumb.cancel_order(desc)

    print( status )
    # print(bithumb.get_current_price("ALL"))

