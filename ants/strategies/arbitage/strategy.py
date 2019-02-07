# -*- coding: utf-8 -*-
import logging
from arbitrage.provider.observers import Observer

class StrategyTypeA(Observer):
    """
    재정거래 확인하는 전략을 넣는다.
    도엽의 ETH 거래를 넣어서 동작하는 것을 검증한다.
    전략 모델 폴더를 만들고 거기에 관련된 함수 및 파일을 넣어서 샘플을 구성한다.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.target_coins = ['KRW-ETH', 'KRW-DASH', 'ETH-DASH', 'KRW-LTC', 'ETH-LTC', 'KRW-STRAT', 'ETH-STRAT', 'KRW-XRP', 'ETH-XRP', 'KRW-ETC', 'ETH-ETC', 'KRW-OMG', 'ETH-OMG', 'KRW-SNT', 'ETH-SNT', 'KRW-WAVES', 'ETH-WAVES', 'KRW-XEM', 'ETH-XEM', 'KRW-ZEC', 'ETH-ZEC', 'KRW-XMR', 'ETH-XMR', 'KRW-QTUM', 'ETH-QTUM', 'KRW-GNT', 'ETH-GNT', 'KRW-XLM', 'ETH-XLM', 'KRW-REP', 'ETH-REP', 'KRW-ADA', 'ETH-ADA', 'KRW-POWR', 'ETH-POWR', 'KRW-STORM', 'ETH-STORM', 'KRW-TRX', 'ETH-TRX', 'KRW-MCO', 'ETH-MCO', 'KRW-SC', 'ETH-SC', 'KRW-POLY', 'ETH-POLY', 'KRW-ZRX', 'ETH-ZRX', 'KRW-SRN', 'ETH-SRN', 'KRW-BCH', 'ETH-BCH', 'KRW-ADX', 'ETH-ADX', 'KRW-BAT', 'ETH-BAT', 'KRW-DMT', 'ETH-DMT', 'KRW-CVC', 'ETH-CVC', 'KRW-WAX', 'ETH-WAX']
        self.data_provider = None
    
    def run(self):
        self.logger.info('strategy run')
        
        
    def register_data_provider(self, provider):
        self.data_provider = provider
        
        #데이터 제공자에게 업데이트 리스너와 요청할 코인을 등록한다
        self.data_provider.register(self, self.target_coins)

    def __perform(self, obu):
        #obu을 사용하여 판정을 한다
        #판정 후 등록된 func를 호출한다
        self.logger.info('perform strategy')
        
    def update(self, args):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy')
        print(args)
        pass
    
    
if __name__ == '__main__':
    print('test')