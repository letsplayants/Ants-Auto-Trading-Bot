import json
import base64
import importlib
import os

from menus.menu_back import BackMenu
from menus.menu_item import MenuItem

from exchangem.crypto import Crypto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

class ExchangeAPIs(MenuItem):
    #API 등록 및 설정
    def __init__(self, exchange_name='upbit'):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(ApiAdd(exchange_name))
        self.__add__(ApiTest(exchange_name))
        self.__add__(ApiDel(exchange_name))
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return 'APIs Key 설정'

    def to_dict(self):
        return 'APIs Key 설정'
        
    def make_menu_keyboard(self, bot=None, chat_id=None, rcv_message = None):
        msg = '{} 거래소 API Key 설정 메뉴입니다'.format(self.exchange_name.upper())
        super().make_menu_keyboard(bot, chat_id, msg)
        
class ApiAdd(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        self.init()
        pass
    
    def init(self):
        #API 입력 차례인지 secret 입력 차례인지 기록한다
        self.secret_input = False
        self.api_key = ''
        self.api_secret = ''
        pass
    
    def __repr__(self):
        return 'API Key 등록'
        
    def to_dict(self):
        return 'API Key 등록'
    
    def make_menu_keyboard(self, bot, chat_id, rcv_message = None):
        if(self.secret_input):
            msg = 'Secret Key를 입력하세요'
        else:
            msg = '{} 거래소 API Key를 입력하세요'.format(self.exchange_name.upper())
            self.secret_input = False
            
        super().make_menu_keyboard(bot, chat_id, msg)
    
    def parsering(self, update, context):
        self.logger.debug('got message : {}'.format(context))
        if(super().parsering(update, context)):
            self.logger.debug('got BACK BUTON message : {}'.format(context))
            return
        
        message = context.message
        text = message.text
        
        if(self.secret_input):
            self.api_secret = text
            self.secret_input = False
            self.do_update(update, context)
        else:
            self.api_key = text
            self.secret_input = True
            msg = 'Secret Key를 입력하세요'.format(self.exchange_name)
            super().make_menu_keyboard(self.bot, self.chat_id, msg)

    def do_update(self, update, context):
        try:
            self.save_apikey()
            message = '{}거래소 API키를 추가 했습니다. \n대화창에 입력된 API Key는 지워주세요'.format(self.exchange_name)
        except Exception as exp:
            message = '오류 : api키 추가중 오류가 발생하였습니다\n{}'.format(exp)
            self.logger.warning(message)
            
        super().make_menu_keyboard(self.bot, self.chat_id, message)
        self.go_back()
    
    def save_apikey(self):
        # 암호화 루틴 불러서 암호화 한 뒤 저장한다
        # TODO ssh키가 없을 경우 자동 생성하여 로컬에 저장한다
        # 현재는 ssh키는 설정되어 있다고 가정한다
        # ssh 키를 사용하여 암호화 한 후 원래 설정대로 저장한다
        
        #파일을 열어서 기존 설정을 읽어온다
        try:
            cp = Crypto()
            keyset = cp.readKey('configs/ants.conf')
            exchanges = self.readKey('configs/exchanges.key')
        except Exception as e:
            self.logger.warning('Crypto except : {}'.format(e))
            raise Exception(e)
            
        try:
            encrypt_key = cp.encrypt(self.api_key)
            encrypt_secret = cp.encrypt(self.api_secret)
            
            encoded = base64.encodebytes(cp.encrypt(self.api_key))
            en_apiKey = encoded.decode('ascii')
            
            encoded = base64.encodebytes(cp.encrypt(self.api_secret))
            en_secret = encoded.decode('ascii')
            
            key_set = {
                'apiKey': en_apiKey,
                'secret': en_secret
            }
            
            new_exchange = self.exchange_name.lower()
            exchanges[new_exchange] = key_set
            
            self.saveConf('configs/exchanges.key', exchanges)
        except Exception as exp:
            self.logger.warning('Crypto except : {}'.format(exp))
            raise Exception('암호화 작업 중 오류가 발생했습니다\n{}'.format(exp))
    
    def readKey(self, filePath):
        if not os.path.isfile(filePath):
            msg = "File path {} does not exist. Will Create.".format(filePath)
            self.logger.warning(msg)
            raise Exception(msg)
        
        try:
            with open(filePath) as fp:
                result = json.load(fp)
        except Exception as exp:
            msg = "Can't load json : {}".format(exp)
            self.logger.warning(msg)
            raise Exception(msg)
        
        return result
        
    def saveConf(self, filePath, data):
        try:
            with open(filePath, 'w+') as fp:
                fp.write(json.dumps(data, sort_keys=True, indent=4))
                
        except Exception as exp:
            msg = "Can't save json : {}".format(exp)
            self.logger.warning(msg)
            raise Exception(msg)    

class ApiTest(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        pass
    
    def init(self):
        pass
    
    def run(self):
        message = ''
        try:
            message = self.do_test()
            message = '테스트 성공 : {}'.format(message)
        except Exception as e:
            message = str(e)
            
        super().make_menu_keyboard(self.bot, self.chat_id, message)
        self.go_back()
        
    def __repr__(self):
        return 'API Key 테스트'
        
    def to_dict(self):
        return 'API Key 테스트'
        
    def do_test(self, coin_name=None):
        self.logger.debug('exchange connection test with key')
        config_file = 'configs/ants.conf'
        
        try:
            # 거래소 클래스를 찾는다
            exchange_class_path = 'exchangem.exchanges.{}'.format(self.exchange_name)
            class_name = self.exchange_name
            class_name = class_name[0].upper() + class_name[1:len(class_name)]
            exchange_setting_conf = 'configs/{}.conf'.format(self.exchange_name)
            self.logger.debug('load class {}\tconfig file : {}\tkey file: {}'.format(class_name, exchange_setting_conf, config_file))
            
            
            #사용할 전략을 만든다
            loaded_module = importlib.import_module(exchange_class_path)
            klass = getattr(loaded_module, class_name)
            exchange = klass({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':exchange_setting_conf})
            self.logger.debug('Text exchange : {}'.format(klass))
            
            
            #코인별 잔고를 찍는다.
            #설정 파일에 설정된 코인의 잔고를 찍는다
            #해당 거래소에 입력된 코인이 없을 수도 있다.
            #이를 대비하여 거래소에 존재하는 코인이나 설정 파일에 설정된 내용을 
            #기반으로 잔고 및 가용 금액을 조회, 테스트 해야한다
            if(coin_name == None):
                coin_name = 'KRW'
                
            balance = exchange.get_balance(coin_name)
            if(balance == None):
                raise Exception('{} is not support {}'.format(exchange, coin_name))
                
            self.logger.debug(exchange.get_balance(coin_name).get_all())
            self.logger.debug('Availabel {} size : {}'.format(coin_name, exchange.get_availabel_size(coin_name)))
            return '사용 가능한 금액 {} : {}'.format(coin_name, exchange.get_availabel_size(coin_name))
        except Exception as exp:
            self.logger.debug('except : {}'.format(exp))
            raise Exception('except : {}'.format(exp))
        

class ApiDel(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        self.DELETE = '삭제'
        pass
    
    def __repr__(self):
        return 'API Key 삭제'
        
    def to_dict(self):
        return 'API Key 삭제'

    def run(self):
        message = '삭제를 원하시면 ''{}'' 라고 입력하세요'.format(self.DELETE)
        super().make_menu_keyboard(self.bot, self.chat_id, message)
        
    def parsering(self, update, context):
        self.logger.debug('got message : {}'.format(context))
        if(super().parsering(update, context)):
            self.logger.debug('got BACK BUTON message : {}'.format(context))
            return
        
        message = ''
        text = context.message.text
        
        deleted = False
        try:
            if(text == self.DELETE):
                self.do_delete()
                message = '삭제하였습니다'
                deleted = True
        except Exception as e:
            message = str(e)
        
        super().make_menu_keyboard(self.bot, self.chat_id, message)
        if(deleted):
            self.go_back()
        
    def do_delete(self):
        exchanges = self.readKey('configs/exchanges.key')
        exchanges[self.exchange_name] = {}
        self.saveConf('configs/exchanges.key', exchanges)
        pass
        
        
    def readKey(self, filePath):
        if not os.path.isfile(filePath):
            msg = "File path {} does not exist. Will Create.".format(filePath)
            self.logger.warning(msg)
            raise Exception(msg)
        
        try:
            with open(filePath) as fp:
                result = json.load(fp)
        except Exception as exp:
            msg = "Can't load json : {}".format(exp)
            self.logger.warning(msg)
            raise Exception(msg)
        
        return result
        
    def saveConf(self, filePath, data):
        try:
            with open(filePath, 'w+') as fp:
                fp.write(json.dumps(data, sort_keys=True, indent=4))
                
        except Exception as exp:
            msg = "Can't save json : {}".format(exp)
            self.logger.warning(msg)
            raise Exception(msg)    
            
if __name__ == "__main__":
    # add = ApiAdd('upbit')
    # add.save_apikey()
    
    # print("\ucd5c\uc18c \uad6c\ub9e4\uc218\ub7c9\uc740 10 AE \uc785\ub2c8\ub2e4.")
    ApiTest('upbit').do_test()
    
    pass