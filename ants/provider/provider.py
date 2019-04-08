# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from ants.provider.observers import ObserverNotifier
from ants.provider.observers import Observer

class Provider(ObserverNotifier):
    """
    거래소나 이메일 정보등 데이터를 수집하여 전략에게 제공해주는 역할
    데이터가 수신되면 옵저버 패턴을 통해 등록된 오브젝트를 callback한다
    그래서 ObserverNotifier를 기본으로 장착하고 있다
    """
    def __init__(self):
        ObserverNotifier.__init__(self)
    
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    