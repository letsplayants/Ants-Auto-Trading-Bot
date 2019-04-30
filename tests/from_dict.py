import json
"""
class from dict

from_dict()함수를 보면됨.
setattr를 사용하여 입력된 dict를 그대로 클래스 변수에 1:1로 넣어버림
이 때 기존에 없던 변수가 신규 추가될 수 있음

"""

class Ex1(object):
    mydic1 = {}
    noShow = {}

    def __init__(self, init_value=None):
        self.mydic2 = {
            'k1' : 'aaa',
            'k2':'bbb',
            'k3': {
                'k3-1':1,
                'k3-2':2
            },
            'k4-arr':[1,2,3,4,5],
            'k5-co':[1,'ab', (1,2), {'a':1}]
        }
        
    def from_dict(self, src):
        if(type(src) is not type({})):
            return
        
        for a, b in src.items():
            # print('key : {}\t,value:{}'.format(a,b))
            setattr(self, a, b)
            
            # if isinstance(b, (list, tuple)):
            #     setattr(self, a, [dict(Ex1(init_value=x)) if isinstance(x, dict) else x for x in b])
            # else:
            #     setattr(self, a, dict(Ex1(init_value=b)) if isinstance(b, dict) else b)
    
    def __iter__(self):
        klass = self.__class__    
        # first start by grabbing the Class items
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        # then update the class items with the instance items
        iters.update(self.__dict__)

        # now 'yield' through the items
        exclucive=['noShow',]
        for x,y in iters.items():
            if(x not in exclucive):
                yield x,y

    def to_file(self, file_name=None):
        import json
        if(file_name is None):
            file_name = 'file.tmp'

        with open(file_name, 'w') as file:
            file.write(json.dumps(dict(self), indent=4, sort_keys=True)) # use `json.loads` to do the reverse

    def from_file(self, file_name=None):
        import json
        if(file_name is None):  
            file_name = 'file.tmp'
            
        with open(file_name, 'r') as file:
            self.from_dict(json.loads(file.read()))

if __name__ == '__main__':
    print('class from dict test')

    ex1 = Ex1()
    print(ex1)
    
    d1 = dict(ex1)['mydic1']
    d2 = dict(ex1)['mydic2']
    d3 = {}
    dd = {
        'mydic1':d2,
        'mydic2':d1,
        'mydic3':d3
    }
    
    print(type({}))
    print(type(dd))
    ex1.from_dict(dd)
    print(dict(ex1))
    
    mydict = dict(ex1)
    print(mydict)
    
    ex1.to_file()
    
    ex2 = Ex1()
    ex2.from_dict({'mydic1':{},'mydic2':{}})
    print(dict(ex2))
    ex2.from_file()
    print(dict(ex2))
    