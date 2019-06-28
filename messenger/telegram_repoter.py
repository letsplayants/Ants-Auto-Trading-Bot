# -*- coding: utf-8 -*-
# https://github.com/python-telegram-bot/python-telegram-bot

from signal import signal, SIGINT, SIGTERM, SIGABRT

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import ants.utils as utils
import logging
import json
import m_emoji as em
from menus.main_menu import MainMenu
from q_publisher import MQPublisher
from q_receiver import MQReceiver
from selfupgrade import CheckForUpdate
from distutils.dir_util import copy_tree
from sh import git
import time
import os, sys
from env_server import Enviroments

from exchangem.model.price_storage import PriceStorage

class TelegramRepoter():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info('TelegramRepoter init...')
        self.menu_string_set()
        
        try:
            self.conf = Enviroments().messenger
            bot_token = self.conf['bot_token']
            if(bot_token is None or bot_token == ''):
                self.conf.load_v1_config()
                bot_token = self.conf['bot_token']
            
            self.bot = telegram.Bot(token=self.conf["bot_token"])
        except Exception as exp:
            self.logger.error('Can''t init telegram bot : {}'.format(exp))
            sys.exit(1)
            return
        
        bot_id = self.conf['bot_id']
        if(bot_id is None or bot_id is ''):
            self.conf['bot_id'] = self.bot.get_me()['username']
            bot_id = self.conf['bot_id']
            Enviroments().save_config()
        
        ck = self.conf.get('use_custom_keyboard')
        if(ck is None):
            self.custom_keyboard = True
        else:
            self.custom_keyboard = False
        
        
        self.exchange_name = Enviroments().qsystem.get_quicktrading_q()
        self.subscriber_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.publisher = MQPublisher(self.exchange_name)
        self.subscriber = MQReceiver(self.subscriber_name, self.sbuscribe_message)
        self.subscriber.start()
        
        self.menu_stack = []
        self.logger.info('Telegram is Ready, {}'.format(self.bot.get_me()))
        self.logger.debug('telegram message q name : {}'.format(self.subscriber_name))
        self.logger.debug('telegram quick trading q name : {}'.format(self.subscriber_name))
        # self.send_message('Telegram Repoter is ready')
        self.run_listener()
        # self.remove_kdb()
        self.make_menu_keyboard()
        
    def save_config(self):
        Enviroments().messenger = self.conf
        Enviroments().save_config()
    
    def sbuscribe_message(self, ch, method, properties, body):
        body =  json.loads(body.decode("utf-8"))
        if(body.find('SHOW ORDER') == 0):
            self.send_message_order(body)
        else:
            self.send_message(body)
      
    def send_message_order(self, msg):
        # msg = msg.replace('SHOW ORDER','')
        msg = msg[msg.find('\n'):]
        
        self.logger.debug('send_msg : {}-{}'.format(self.conf['chat_id'], msg))
        self.bot.sendMessage(self.conf['chat_id'], msg, reply_markup=self.order_keyboard())
    
    def order_keyboard(self):
        keyboard = [[InlineKeyboardButton("주문 취소", callback_data='cancel_order')]]

        if(self.custom_keyboard):
            return InlineKeyboardMarkup(keyboard)
        else:
            return telegram.ReplyKeyboardRemove()
    
    def menu_string_set(self):
        self.menu = MainMenu()
    
    def make_menu_keyboard(self, bot = None, chat_id = None):
        keyboard = []
        for item in self.menu:
            keyboard.append(InlineKeyboardButton(item))

        #ReplyKeyboardMarkup는 callback 기능이 없다.
        #그러므로 문구가 메뉴 호출에 해당한다
        #봇이 제공하는 버튼은 사용자가 채팅을 치는 것을 대신할 뿐이다.
        #봇이 버튼에서 '인사'라는 버튼을 제공한다면 사용자는 버튼을 누르는 것 대신 '인사'라고 쳐도 봇은 동일하게 동작한다
        
        if(Enviroments().etc.get('test_mode') == True):
            mode_str = '테스트 모드'
        else:
            mode_str = '실전 모드'
            
        support_exchange_list = 'upbit'
        
        self.welcome_message = """
        안녕하세요,\n\n버전 : {}\n동작 모드 : {}\n지원 거래소 : {}\n이 화면에서만 퀵매매가 동작합니다.
        """.format(
            '개발 버전(git commit id표시)',
            mode_str,
            support_exchange_list)
        
        if(self.custom_keyboard):
            reply_markup = telegram.ReplyKeyboardMarkup(self.build_menu(keyboard, n_cols=2))
        else:
            reply_markup = None
            
        self.bot.send_message(chat_id=self.conf['chat_id'], text=self.welcome_message, reply_markup=reply_markup)
  
    def check_authorized(self, from_who):
        from_id = str(from_who['id'])
        
        if(self.conf['chat_id'] == from_id):
            return True
        elif(from_id in self.conf['authorized']):
            return True
        else:
            self.logger.warning('Unauthorized user send to command - input:{}\tchat_id:{}'.format(from_who, self.conf['chat_id']))
            return False
        
    def message_parser(self, bot, update):
        self.logger.debug('got some message')
        #1:1 에서 메시지 수신시
        #update : {'update_id': 371978001, 'message': {'message_id': 12490, 'date': 1561387246, 'chat': {'id': 444609550, 'type': 'private', 'username': 'lemy0715', 'first_name': 'LeMY'}, 'text': '123', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 444609550, 'first_name': 'LeMY', 'is_bot': False, 'username': 'lemy0715', 'language_code': 'ko'}}, '_effective_message': {'message_id': 12490, 'date': 1561387246, 'chat': {'id': 444609550, 'type': 'private', 'username': 'lemy0715', 'first_name': 'LeMY'}, 'text': '123', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 444609550, 'first_name': 'LeMY', 'is_bot': False, 'username': 'lemy0715', 'language_code': 'ko'}}}

        #그룹 대화방에서 메시지 수신
        #현재 설정으로 메시지를 못 받는듯
        
        #channel에서 메시지 수신시
        #update : {'update_id': 371978003, 'channel_post': {'message_id': 3, 'date': 1561387474, 'chat': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}, 'text': '채널 메시지', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False}, '_effective_message': {'message_id': 3, 'date': 1561387474, 'chat': {'id': -1001207026903, 'type': 'channel', 'title': '개발테스트용'}, 'text': '채널 메시지', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False}}

        self.logger.debug('update : {}'.format(update))
        
        if(update.channel_post is not None):
            #channel post
            message = {
                'text' : update.channel_post.text,
                'from' : update.channel_post.chat
            }
        elif(update.message is not None): 
            #1:1 message
            message = {
                'text' : update.message.text,
                'from' : update.message.chat
            }
        else :
            return
            
        if(not self.check_authorized(message['from'])):
            return
        
        # try:
        #     message = update.message
        #     text = message.text
        #     self.logger.debug(text)
        # except Exception as exp:
        #     #그룹 대화방이나 1:1 대화방이 아닌 경우 오류가 발생함
        #     self.logger.debug(update)
        #     self.logger.debug(update.channel_post.text)
        #     text = update.channel_post.text
        
        menu_item = None
        for item in self.menu:
            item_txt = str(item)
            if(item_txt == message['text']):
                self.logger.debug("item : {}\t text: {}\t{}".format(item_txt, message['text'], (item_txt == message['text'])))
                menu_item = item
                self.menu_stack.append(item)
                break;
        
        self.logger.debug('fined item : {}'.format(menu_item))
        if(menu_item is None):
            self.check_quick_trading(message)
            return
        
        # 방법1. 동작안함. dp.restart 해야하는데, stop이후 start하면 뻗음.. 설령 stop이 된다고 하더라도 내부적으로 thread라 join되는데 기다리는데 시간이 많이 걸림
        # 현재 메시지 처리기를 지우고 하위 메뉴의 메시지 처리기를 등록해준다
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/dispatcher.py
        dp = self.updater.dispatcher
        
        menu_item.init()
        menu_item.set_bot_n_chatid(self.bot, self.conf['chat_id'])
        # menu_item.set_previous_message_handler(dp, self.message_handler)
        menu_item.set_previous_keyboard(self.make_menu_keyboard)
        menu_item.set_previous_item(None, dp, self.message_handler)
        menu_item.make_menu_keyboard(self.bot, self.conf['chat_id'])
        
        dp.add_handler(menu_item.message_handler)
        dp.remove_handler(self.message_handler)
        
        menu_item.run()
        # menu_item.parsering(update, text)
        
    def check_quick_trading(self, message):
        self.logger.debug('check_quick_trading got message : {}'.format(message))
        try:
            text = message['text'].split(' ')
            action = text[0].strip().lower()
            
            if((action in ['buy', 'sell', 'show']) == False):
                return
        except Exception as exp:
            self.logger.debug('check_quick_trading header paring Exception : {}'.format(exp))
            return
        
        try:
            self.logger.debug('check quick trading msg : {}'.format(action))
            # text = text.split(' ')
            ret = {}
            ret['version'] = 3
            command = ret['command'] = text[0].strip().upper()
            
            if(command in ['BUY', 'SELL']):
                ret['exchange'] = text[1].strip().upper()
                ret['market'] = text[2].strip().upper()
                ret['coin'] = text[3].strip().upper()
                ret['price'] = text[4].strip()
                ret['seed'] = text[5].strip()
                ret['etc'] = {}
                ret['etc']['from'] = eval(str(message['from']))
            else:
                if(command in ['SHOW']):
                    ret['sub_cmd'] = text[1].strip().upper()
                    ret['exchange'] = text[2].strip().upper()
                    try:
                        ret['coin_name'] = text[3].strip().upper()
                    except Exception:
                        ret['coin_name'] = ''
            
            self.publisher.send(ret)
        except Exception as exp:
            self.logger.debug('check_quick_trading body paring Exception : {}'.format(exp))
            return
        
        self.send_message('요청 하신 내용을 수행중입니다')
        pass
    
    def build_menu(self,
               buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu
    
    def remove_kdb(self):
        """
        사용할 일 없을듯.
        """
        reply_markup = telegram.ReplyKeyboardRemove()
        self.bot.send_message(chat_id=self.conf['chat_id'], text="I'm back.", reply_markup=reply_markup)
    
    
    def run_listener(self):
        self.updater = Updater(self.conf['bot_token'])
        
        dp = self.updater.dispatcher
        
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("menu", self.menu_func))
        dp.add_handler(CommandHandler("price", self.show_price))
        dp.add_handler(CommandHandler("upgrade", self.do_upgrade))
        dp.add_handler(CallbackQueryHandler(self.whoami, pattern='whoami'))
        dp.add_handler(CallbackQueryHandler(self.roominfo, pattern='roominfo'))
        dp.add_handler(CallbackQueryHandler(self.welcome, pattern='welcome'))
        dp.add_handler(CallbackQueryHandler(self.cancel_order, pattern='cancel_order'))
        
        # self.message_handler = MessageHandler(Filters.text, self.message_parser)
        self.message_handler = MessageHandler(Filters.text, self.message_parser)
        dp.add_handler(self.message_handler)
        
        # log all errors
        dp.add_error_handler(self.error)
        
        # Start the Bot
        # 내부적으로 쓰레드로 처리된다.
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/updater.py
        self.updater.start_polling(timeout=10, clean=True)
        # self.updater.idle()
    
    def stop(self):
        self.stop_listener()
        
    def stop_listener(self):
        self.logger.info('telegram will be stop')
        self.updater.stop()
        self.updater.signal_handler(SIGTERM, 0)
    
    def show_price(self, update, context):
        self.logger.debug(f'update:{update}')
        self.logger.debug(f'context:{context}')
        # from exchangem.model.pricest_storage import pricestStorage
        ps = PriceStorage()
        price = ps.get_price('UPBIT', 'KRW', 'BTC')
        self.send_message(price)
        
        
    def menu_func(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        
        context.message.reply_text('Please choose:', reply_markup=self.menu_keyboard())
        
    def menu_keyboard(self):
        keyboard = [[InlineKeyboardButton("내 ID 정보", callback_data='whoami'),
                    InlineKeyboardButton("현재 방 정보", callback_data='roominfo')],
                    [InlineKeyboardButton("환영 인사", callback_data='welcome')]]
        if(self.custom_keyboard):
            return InlineKeyboardMarkup(keyboard)
        else:
            return None
        
    def button(self, update, context):
        query = context.callback_query
        query.edit_message_text(text="Selected option: {}".format(query.data))
    
        
    def send_message(self, msg):
        self.logger.debug('send_msg : {}-{}'.format(self.conf['chat_id'], msg))
        self.bot.sendMessage(self.conf['chat_id'], msg)
    
    def roominfo(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        
        query = context.callback_query
        
        self.edit_message(update, query, '방(Group) 속성 : {}\n Group id : {}'.format(query.message.chat.type, query.message.chat.id))
        
        
    def whoami(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        
        print('get message in whoami')
        query = context.callback_query
        if(query.message.chat.type != 'private'):
            self.edit_message(update, query, '1:1방에서만 설정 가능합니다')
            return
        self.edit_message(update, query, '당신의 ID : {}'.format(query.message.chat.id))

    def cancel_order(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        
        message = context.callback_query.message.text
        
        self.logger.debug('cancel order msg : {}'.format(context))
        self.logger.debug('cancel order msg : {}'.format(context.callback_query.message.text))
        
        txt_list = message.splitlines()
        self.logger.debug('cancel order msg : {}'.format(txt_list[0]))
        
        
        exchange = txt_list[0].replace('거래소 : ','')
        order_id = txt_list[1].replace('ID : ', '')
        
        
        ret = {}
        ret['version'] = 2
        command = ret['command'] = 'CANCEL'
        
        ret['sub_cmd'] = 'ORDER'
        ret['exchange'] = exchange
        ret['id'] = order_id
        
        self.publisher.send(ret)
        
        # query = context.callback_query
        # if(query.message.chat.type != 'private'):
        #     self.edit_message(update, query, '1:1방에서만 설정 가능합니다')
        #     return
        # self.edit_message(update, query, '당신의 ID : {}'.format(query.message.chat.id))

    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg,
                        reply_markup=self.menu_keyboard())
    
    def welcome(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        query = context.callback_query
        
        user = query.from_user
        msg = '환영합니다. {}님'.format(user.first_name)
        self.edit_message(update, query, msg)
    
    def error(self, bot_info, update, message):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', bot_info, message)
    
    def do_upgrade(self, update, context):
        if(not self.check_authorized(message['from'])):
            return
        
        self.send_message('업그레이드를 진행합니다\n 업그레이드하는데 약 3~5분 가량 걸리며 완료되면 텔레그램 봇이 재시작 됩니다')
        
        #TODO 프로그램이 실행된 경로를 찾아서 .. 프로젝트 시작 경로를 찾아서 업데이트하도록 한다
        gitDir = os.getcwd() + '/'
        backup_path = gitDir + '/../config_backup_' + self.conf['bot_id']
        
        try:
            # config 폴더를 다른곳에 백업해둔 뒤 업데이트 후 다시 덮어 쓰도록 한다
            self.send_message('설정 백업 중입니다')
            copy_tree(gitDir+'configs', backup_path)
            
            if CheckForUpdate(gitDir):
                self.send_message("업데이트 중입니다")
                # resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--hard", "origin/dev")
                resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--hard", "origin/dev")
                self.send_message(str(resetCheck))
            
            self.send_message('설정 복구 중입니다')
            copy_tree(backup_path, gitDir+'configs')
            
            self.send_message('패키지 업데이트 중입니다')
                
            # import subprocess
            # pip_command = 'pip install -U -r requirements.txt'
            # p = subprocess.Popen(pip_command.split(), stdout=subprocess.PIPE, shell=False)
            # p_status = p.wait()
            
            self.send_message('시스템을 재시작합니다')
            self.send_message('보통 1분안에 완료가 됩니다. 최대 3분까지 기다려보시고 응답이 없으면 업그레이드 실패로 판단하시면 됩니다.')
            self.send_message('업그레이드 실패시 텔레그램에서 복구 불가능하며 담당자에게 문의해주세요')
            time.sleep(2)
            
            upgrade_q = Enviroments().qsystem.get_upgrade_q()
            self.logger.debug('upgrade q : {}'.format(upgrade_q))
            publisher = MQPublisher(upgrade_q)
            publisher.send('restart')
            
            #리스타트는 모니터링 프로세스에게 요청한다
            # try:
            #     import signal
            #     ret = os.kill(os.getpid(), 3)
            #     print('ret:{}'.format(ret))
            # except SystemExit:
            #     self.logger.error("sys.exit() worked as expected")
            # except Exception as exp:
            #     self.logger.error("Something went horribly wrong : ".format(exp)) # some other exception got raised
            
        except Exception as exp:
            self.send_message('업그레이드 실패 : \n{}'.format(exp))
            self.logger.error('업그레이드 실패 : \n{}'.format(exp))

if __name__ == '__main__':
    print('strategy test')
    Enviroments().load_config()
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.updater").setLevel(logging.WARNING)
    logging.getLogger("telegram.bot").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.dispatcher").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)
    
    tel = TelegramRepoter()
    
    # tel.check_quick_trading('buy upbit krw strom 10 10000')

    tel.send_message("봇클래스 테스트.")

    import signal
    from time import sleep
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        # w.stop()
        tel.stop_listener()
        logger.info('Program Exit')

    signal.signal(signal.SIGINT, signal_handler)
