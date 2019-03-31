from menus.m_iter import MIterators

class Setting(MIterators):
    def __init__(self):
        pass
    
    def __repr__(self):
        return '설정'
    
    def to_dict(self):
        """
        텔레그램 인라인 키보드에서 json으로 변환할 때 to_dict를 호출함
        이 때 리턴되는 문자열을 인라인 키보드에서 표시함
        """
        return '설정'
        
        
        