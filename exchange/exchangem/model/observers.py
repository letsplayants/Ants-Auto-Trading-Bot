# -*- coding: utf-8 -*-
import logging
from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def attach(self):
        pass

    @abstractmethod
    def detach(self):
        pass

    @abstractmethod
    def notify(self):
        pass

class Observer:
    def __init__(self):
        print('call init {}'.format(self))
        
    @abstractmethod
    def update(self, args):
        pass

class ObserverNotifier():
    def __init__(self):
        self._observers = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        print('call init {}'.format(self))
        
    def attach(self, observer):
        #observer 타입인지 확인 후 넣는다.
        self.logger.info('attach : {} in {}'.format(observer, self))
        if not isinstance(observer, Observer):
            self.logger.warning('this is not observer {} {}'.format(observer, self))
            return
        
        if observer not in self._observers:
            self._observers.append(observer)
            self.logger.debug('add {}'.format(observer))
            self.logger.debug('added : {} in {}'.format(observer, self))

    def detach(self, observer):
        try:
            self._observers.remove(observer)
            self.logger.debug('remove {}'.format(observer))
        except ValueError as exp:
            self.logger.warning(exp)

    def notify(self, arg=None):
        for observer in self._observers:
            self.logger.debug('updated : {}'.format(observer))
            observer.update(arg)
            self.logger.debug('update {}'.format(observer))

    
   