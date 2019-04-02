class MIterators():
    def __init__(self):
        self.m_list = []
        self.__iter_index__ = 0
        pass

    def __add__(self, item):
        # print('self : {}\tm_list:{}\tadd : {}\t id : {}'.format(id(self), id(self.m_list), item, id(self.__iter_index__)))
        self.m_list.append(item)

    def __iter__(self):
        self.__iter_index__ = 0
        # print('iter - self id : {}\t m_list:{}\titer id : {}\t value : {}'.format(id(self), id(self.m_list), id(self.__iter_index__), self.__iter_index__))
        return self
    
    def __next__(self):
        # print('next - self id : {}\t m_list:{}\titer id : {}\t value : {}'.format(id(self), id(self.m_list), id(self.__iter_index__), self.__iter_index__))
        ret = self.__iter_index__
        if(ret >= len(self.m_list)):
            raise StopIteration
        
        self.__iter_index__ += 1
        return self.m_list[ret]