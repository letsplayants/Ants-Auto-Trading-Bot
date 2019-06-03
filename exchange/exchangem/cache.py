# -*- coding: utf-8 -*-
import logging
import time
import sys


class Cache():
    def __init__(self, expires=None):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('cache ready')
        self.memory = {}
        if(expires == None):
            expires = 30
        self.__expires_sec__ = expires
        pass
    
    def to_key(self, *input_args):
        key = ''
        for arg in input_args:
            key += str(arg)
        
        key = hash(key)
        return key
        
    
    def get_cache(self, key):
        method_name = sys._getframe(1).f_code.co_name
        ret = self.memory.get(method_name)
        if(ret == None):
            return False, None
        
        ret = ret.get(key)
        if(ret == None):
            return False, None
        
        cached_time = ret['time']
        if(time.time() - cached_time >= self.__expires_sec__):
            return False, None
        
        if(len(ret['data']['data']) == 1):
            self.logger.debug('cache hit')
            return True, ret['data']['data'][0]
        
        if(ret['data']['isNone']):
            return False, None
        
        r=[]
        for item in ret['data']['data']:
            r.append(item)
            
        self.logger.debug('cache hit')
        r.insert(0, True)
        return tuple(r)
        
    
    def set_cache(self, key, *data):
        method_name = sys._getframe(1).f_code.co_name
        m = self.memory.get(method_name)
        if(m is None):
            self.memory[method_name] = {}
            m = self.memory[method_name]
        
        isNone = False
        if(data is None):
            isNone = True
        
        m[key] = {}
        m[key]['data'] = {'data':data, 'isNone':isNone}
        m[key]['time'] = time.time()
        
    
if __name__ == '__main__':
    print('Cache module test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    #테스트의 경우 한 메소드(main)에서 입력값만 바뀌고 여러번 호출하게 된다
    #아래의 캐싱은 모두 같은 메소드에서 입력값만 바뀌면서 테스트하는 셈이다
    cache = Cache(60)
    
    # print('-'* 120)
    # key = cache.to_key(1,2,3)
    # result1 = 'result1'
    # cache.set_cache(key, result1)
    # cached, cResult = cache.get_cache(key)
    # if(cached == True):
    #     print('cached')
    # else:
    #     print('not cached')
        
    # if(cResult != result1):
    #     print(f'{cResult} is not match {result1}')
    
    # print('-'* 120)
    
    # key = cache.to_key(1,2,3)
    # result1 = 'result1'
    # cached, cResult = cache.get_cache(key)
    # if(cached == True):
    #     print('cached')
    # else:
    #     print('not cached')
    # if(cResult != result1):
    #     print(f'{cResult} is not match {result1}')
    # print('-'* 120)
        
    m_name = 'method_name1'
    key = cache.to_key(1,2,3)
    result1 = 'result1'
    result2 = 'result2'
    cache.set_cache(key, result1, result2)    
    
    ret = cache.get_cache(key)
    cached, cResult, cResult2 = cache.get_cache(key)
    if(cached == True):
        print('cached')
    else:
        print('not cached')
    if(result1 != cResult or result2 != cResult2):
        print('method_name2 is not match')
    
    print('-'* 120)
    
    # m_name = 'method_name1'
    # key = cache.to_key(1,2,3)
    # result1 = None
    # cache.set_cache(key, result1)
    # cResult = cache.get_cache(key)
    # print(cResult)
    
    # if(cache.get_cache(key) != result1):
    #     print('method_name 1 is not match')
    # print('-'* 120)
    
    # m_name = 'method_name1'
    # key = cache.to_key(1,2,3)
    # result1 = 'result1'
    # cache.set_cache(key, result1)
    # time.sleep(4)
    # cResult = cache.get_cache(key)
    # print(cResult)
    
    # if(cache.get_cache(key) != result1):
    #     print('method_name 1 is not match')
    # print('-'* 120)


    # Timeout 테스트는 하지 않는다.
    # m_name = 'method_name1'
    # key = cache.to_key(1,2,3)
    # result1 = 'result1'
    # cache.set_cache(key, result1)
    # time.sleep(65)
    # cResult = cache.get_cache(key)
    # print(cResult)
    
    # if(cache.get_cache(key) != result1):
    #     print('method_name 1 is not match')
    # print('-'* 120)