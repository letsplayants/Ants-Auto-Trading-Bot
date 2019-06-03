# -*- coding: utf-8 -*-
import logging
import time

class Cache():
    def __init__(self, class_name):
        self.memory = {}
        self.expires_sec = 60   #기본은 60초간 캐싱한다
        pass
    
    def to_key(self, *input_args):
        key = ''
        for arg in input_args:
            key += str(arg)
        
        key = hash(key)
        return key
        
    
    def get_cache(self, method_name, key):
        ret = self.memory.get(method_name)
        if(ret == None):
            return None
        
        ret = ret.get(key)
        if(ret == None):
            return None
        
        cached_time = ret['time']
        if(time.time() - cached_time >= self.expires_sec):
            return None
        
        if(len(ret['data']) == 1):
            return ret['data'][0]
        
        r=[]
        for item in ret['data']:
            r.append(item)
            
        return tuple(r)
        
    
    def set_cache(self, method_name, key, *data):
        m = self.memory.get(method_name)
        if(m is None):
            self.memory[method_name] = {}
            m = self.memory[method_name]
        
        m[key] = {}
        m[key]['data'] = data
        m[key]['time'] = time.time()


    
if __name__ == '__main__':
    print('Cache module test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    cache = Cache('Test1')
    
    m_name = 'method_name1'
    key = cache.to_key(1,2,3)
    result1 = 'result1'
    cache.set_cache(m_name, key, result1)
    
    cResult = cache.get_cache(m_name, key)

    if(cache.get_cache(m_name, key) != result1):
        print('method_name 1 is not match')
    
    print('-'* 120)
    
    
    m_name = 'method_name1'
    key = cache.to_key(1,2,3)
    result1 = 'result1'
    result2 = 'result2'
    cache.set_cache(m_name, key, result1, result2)    
    
    cResult, cResult2 = cache.get_cache(m_name, key)
    if(result1 != cResult or result2 != cResult2):
        print('method_name2 is not match')
    
    print('-'* 120)
    
    m_name = 'method_name1'
    key = cache.to_key(1,2,3)
    result1 = 'result1'
    cache.set_cache(m_name, key, result1)
    time.sleep(4)
    cResult = cache.get_cache(m_name, key)
    print(cResult)
    
    if(cache.get_cache(m_name, key) != result1):
        print('method_name 1 is not match')
    print('-'* 120)

    m_name = 'method_name1'
    key = cache.to_key(1,2,3)
    result1 = 'result1'
    cache.set_cache(m_name, key, result1)
    time.sleep(65)
    cResult = cache.get_cache(m_name, key)
    print(cResult)
    
    if(cache.get_cache(m_name, key) != result1):
        print('method_name 1 is not match')
    print('-'* 120)