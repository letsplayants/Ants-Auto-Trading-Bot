import json
import base64

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
        
    def make_menu_keyboard(self, bot, chat_id, rcv_message = None):
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
            self.secret = text
            self.secret_input = False
            self.do_update(update, context)
        else:
            self.api_key = text
            self.secret_input = True
            msg = 'Secret Key를 입력하세요'.format(self.exchange_name)
            super().make_menu_keyboard(self.bot, self.chat_id, msg)

    def do_update(self, update, context):
        message = '{}거래소 API키를 추가 했습니다. \n대화창에 입력된 API Key는 지워주세요'.format(self.exchange_name)
        self.save_apikey()
        super().make_menu_keyboard(self.bot, self.chat_id, message)
        self.go_back()
    
    def save_apikey(self):
        # 암호화 루틴 불러서 암호화 한 뒤 저장한다
        # TODO ssh키가 없을 경우 자동 생성하여 로컬에 저장한다
        # 현재는 ssh키는 설정되어 있다고 가정한다
        # ssh 키를 사용하여 암호화 한 후 원래 설정대로 저장한다
        
        #파일을 열어서 기존 설정을 읽어온다
        cp = Crypto()
        keyset = cp.readKey('configs/ants.conf')
        try:
            exchanges = self.readKey('configs/exchange.key')
        except :
            exchanges = {}
            
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
            
            self.saveConf('configs/exchange.key', exchanges)
        except Exception as exp:
            self.logger.warning('Crypto except : {}'.format(exp))
            raise Exception('암호화 작업 중 오류가 발생했습니다')
    
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
    
    def __repr__(self):
        return 'API Key 테스트'
        
    def to_dict(self):
        return 'API Key 테스트'

class ApiDel(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return 'API Key 삭제'
        
    def to_dict(self):
        return 'API Key 삭제'


if __name__ == "__main__":
    add = ApiAdd('upbit1')
    add.save_apikey()
    