# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

from messenger.q_publisher import MQPublisher
from exchangem.model.coin_model import CoinModel

class BaseClass():
	pass

class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]
		
class Enviroments(BaseClass, metaclass=Singleton):
    """
    모든 설정을 여기서 메모리에 들고 있으면서 관리한다
    모든 설정은 파일에 기록될 때 ants.conf를 제외하고 모두 암호화 된다.
    설정 값을 입력할 때도 cli를 통해서 설정한다. 더 이상 파일을 직접 수정한 설정은 없다
    설정 값 중 키 값은 암호화 되지 않는다. 값 부분만 모두 암호화 된다.
    
    대표적 기록 값
    - 프로젝트 경로
    - 거래소 데이터
    - 각종 큐 경로
    """
    DEFAULT_CONF='configs/ants.conf'
    AUTO_CONF='configs/ant_auto.conf'
    
    #구동 시스템에 관한 정보
    sys = {}
    common = {}
    exchanges = {}
    strategies = {}
    messenger = {}
    qsystem = {}
    #사용자가 지정한 트레이딩 대상 코인을 지정함
    trading = {}
    etc = {}
    
    init_load = True
    
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.first_exception = True

    def __repr__(self):
        return str(dict(self))
        
    def from_dict(self, src):
        if(type(src) is not type({})):
            return
        
        for a, b in src.items():
            setattr(self, a, b)
            self.logger.debug('a:{}\tb:{}'.format(a,b))
        
    def __iter__(self):
        klass = self.__class__
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        include=['sys', 'common', 'exchanges', 'messenger', 'etc', 'strategies']
        for x,y in iters.items():
            if(x in include):
                yield x,y

    def save_config(self, file_name=None):
        if(file_name is None):
            file_name = self.AUTO_CONF

        with open(file_name, 'w') as file:
            file.write(json.dumps(dict(self), indent=4, sort_keys=True))

    def load_config(self, file_name=None):
        if(file_name is None):
            file_name = self.AUTO_CONF
            
        self.logger.debug('file_name : {}'.format(file_name))
        try:
            with open(file_name, 'r') as file:
                rdict = json.loads(file.read())
                self.from_dict(rdict)
                self.logger.debug('rdict : {}'.format(type(rdict)))
        except Exception as e:
            if(self.first_exception):
                self.first_exception = False
                self.logger.info('Can''t load auto config. Will load default config : {}'.format(e))
                
                if(self.load_config_ver1(self.DEFAULT_CONF)):
                    self.set_default()
                    self.save_config()
                    return
                else:
                    self.load_config(self.DEFAULT_CONF)
            else:
                self.logger.error('Can''t load default config. : {}'.format(e))
                sys.exit(1)
        
        for k, v in self.exchanges.items():
            self.logger.debug('key : {}\tv:{}'.format(k, v))
            
        self.check_default()
    
    def check_default(self):
        #초기값이 반드시 있어야하는 변수들을 여기서 선언한다
        if(self.etc.get('test_mode') is None):
            self.etc['test_mode'] = 'True'
        
        ExchangesEnv().check_default()
        
        for k, v in self.exchanges.items():
            self.logger.debug('key : {}\tv:{}'.format(k, v))
        
        
    def load_config_ver1(self, file_name):
        """
        구버젼 config 포멧을 읽어들인다
        구버젼이면 True, 아니면 False를 리턴한다
        """
        try:
            with open(file_name, 'r') as file:
                rdict = json.loads(file.read())
                self.logger.debug(rdict['key_file']['rsa_key_file'])
                item = {
                    'common':rdict
                }
                self.from_dict(item)
                self.logger.debug('load config version 1 : {}'.format(item))
        except Exception as e:
            self.logger.debug('exception : {}'.format(e))
            return False
        
        return True
    
    
class ExchangesEnv(BaseClass, metaclass=Singleton):
    """
    거래소 관련 환경 값을 가지고 있는다
    Enviroments의 exchanges를 레퍼런스 참조하는 방식으로 설계 및 구현한다
    exchanges에 관련된 값을 조회/조작하는 기능을 제공한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.exchanges = Enviroments().exchanges
        
    def __repr__(self):
        return str(dict(self))
    
    def check_default(self):
        exc = Enviroments().exchanges
        if(len(exc) is 0):
            self.set_default()
            return
        
        if(exc.get('default') is None):
            exc['default'] = self.get_default_setting()
        
        for k, v in exc.items():
            if(v.get('trading_list') is None):
                self.logger.debug('{}:{} is None'.format(k, v))
                v['traing_list'] = {'all' : True, 'list' : []}
            if(v.get('coin') is None):
                coin = CoinModel()
                coin.amount.available = 1000
                coin.amount.keep = 0
                v['coin'] = {'krw' : dict(coin)}
        
        
    def set_default(self):
        #있어야하는 값들이 다 있는지 확인 후 없으면 초기화 한다
        Enviroments().exchanges = {}
        self.exchanges = Enviroments().exchanges
        self.exchanges['default'] = self.get_default_setting()
    
    def get_default_setting(self):
        coin = CoinModel()
        coin.amount.available = 1000
        coin.amount.keep = 0
        
        coins = {
            'krw' : dict(coin)
        }
        
        keys = {
            'apiKey':'',
            'secret':''
        }
        
        trading_list = {
            'all' : True,
            'list' : []
        }
        
        default_setting = {
            'coin' : coins,
            'keys' : keys,
            'trading_list' : trading_list
        }
        
        return default_setting
    
    def getExchange(self, name):
        if(self.exhcnages.get(name) is None):
            self.exhcnages[name] = self.default_setting()
        return self.exchanges[name]
    
    def get_trading_list(self, name):
        if(self.exchanges.get(name).get('trading_list') is None):
            self.exchanges[name]['trading_list'] = {'all' : True, 'list' : []}
        return self.exchanges[name]['trading_list']


if __name__ == '__main__':
    print('Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    
    import os
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    Enviroments().load_config(path)
    
    print(type(ExchangesEnv().get_trading_list('default')))
    print(type(ExchangesEnv().get_trading_list('default').get('list')))
    print(ExchangesEnv().get_trading_list('default').get('list'))
    print('btc' in ExchangesEnv().get_trading_list('default').get('list'))
    
    coin_name = 'btcx'
    if(ExchangesEnv().get_trading_list('default').get('all') != True):
        if(coin_name not in ExchangesEnv().get_trading_list('default').get('list')):
            print('{} is not in trading list'.format(coin_name))
            
    
    # en1 = Enviroments()
    # en2 = Enviroments()
    
    # en1.common['ssh_pub'] = '~\pi\.ssh\id_rsa.pub'
    
    # print(dict(en1))
    
    # f_name = 'test_conf.tmp'
    # en1.save_config(f_name)
    
    # en1.load_config(f_name)
    
    # en1.from_dict
    
    # print(dict(en1))
    
    # print(consts.ENV)
    # print(en1)
    # print(en1.common)
    # print(en2.common)

    # dt = vars(en1)
    # print(dt)

    # j = en1.to_json()
    # print(j)
    
    # en1.from_json(j)