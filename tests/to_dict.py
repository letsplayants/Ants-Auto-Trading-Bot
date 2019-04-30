import json
"""
class to dict

결론 : 
Ex1을 베이스 삼아 class to dict로 사용하면됨

https://docs.python.org/ko/3.6/tutorial/classes.html


키는 __iter__()함수임.
Foo()는 dict key이름을 내부 변수와 다르게 사용하고 싶을때
"""
class Foo():
    def __init__(self):
        self.co = {}
        self.ex = {}
        pass
    
    def __iter__(self):
        yield 'a', self.co
        yield 'b', self.ex
    
class A(object):
    d = '4'
    e = '5'
    f = '6'

    def __init__(self):
        self.a = '1'
        self.b = '2'
        self.c = '3'

    def __iter__(self):
        # first start by grabbing the Class items
        iters = dict((x,y) for x,y in A.__dict__.items() if x[:2] != '__')

        # then update the class items with the instance items
        iters.update(self.__dict__)

        # now 'yield' through the items
        for x,y in iters.items():
            yield x,y

class Ex1(object):
    mydic1 = {}

    def __init__(self):
        self.mydic2 = {'k1' : 'aaa',
            'k2':'bbb',
            'k3': {
                'k3-1':1,
                'k3-2':2
            },
            'k4-arr':[1,2,3,4,5],
            'k5-co':[1,'ab', (1,2), {'a':1}]
        }
        
    def __iter__(self):
        klass = self.__class__
        # first start by grabbing the Class items
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        # then update the class items with the instance items
        iters.update(self.__dict__)

        # now 'yield' through the items
        for x,y in iters.items():
            yield x,y


if __name__ == '__main__':
    print('Json conveter test')
    
    mydict = {
        'a' : 'abc',
        'b' : 1
    }
    json.dumps(mydict)
# ------------------------------------------------------------------------    
    mydict['_dict'] = {'a':'abcd','b':123}
    print(json.dumps(mydict))
# ------------------------------------------------------------------------
    ff = Foo()
    #vars 호출하는거 동작안함
    print('vars : '.format(vars(ff)))
    print(ff.__dict__)
    
    df = dict(ff)
    print(df)
    # json.dumps(ff)
# ------------------------------------------------------------------------
    a = A()
    print(a.__dict__)
    print(dict(a))
# ------------------------------------------------------------------------
    print('EX1 test')
    ex1 = Ex1()
    print(ex1)
    print(dict(ex1))
# ------------------------------------------------------------------------
    