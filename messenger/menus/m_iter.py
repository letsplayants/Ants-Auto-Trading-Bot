class MIterators():
    m_list = []
    __iidx__ = 0
    
    def __init__(self):
        pass

    def __add__(self, item):
        self.m_list.append(item)

    def __iter__(self):
        self.__iidx__ = 0
        return self.m_list[self.__iidx__]
    
    def __next__(self):
        ret = self.__iidx__
        if(ret >= len(self.m_list)):
            raise StopIteration
        
        self.__iidx__ += 1
        return self.m_list[ret]