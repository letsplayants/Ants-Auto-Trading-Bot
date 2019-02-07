# -*- coding: utf-8 -*-
import logging

class Repoter():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass
    
    def register_exchange(exchange):
        self.exchange(exchange)
    
    def register_do_func(func):
        func_list.append(func)
    
    def do_monitor(self):
        #thread로 돌면서 오더가 완료되었는지 확인한다
        #오더가 완료되었으면 로깅하고 등록된 콜체인을 불러준다
    