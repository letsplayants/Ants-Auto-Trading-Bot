import time
import datetime
import pytz

ttime = datetime.datetime.now(pytz.timezone('Asia/Seoul')) 
nowDate = ttime.strftime('%Y-%m-%d %H:%M')
print(nowDate)

#하루는 1440분이다.
#3, 5, 10, 15, 30, 40, 45, 60분으로 하루를 나누면 딱 맞게 떨어진다.
#입력된 시간에 맞는 스케쥴러에 함수를 등록한다
#현재 시간으로 부터 지정된 다음 시간이 되면 그 때 주기적으로 동작하는 함수를 등록한다
#ex) 현재 17:20분인데 30분 스케쥴러가 등록되면 10분뒤부터 30분 단위로 동작하는 스케쥴러를 등록한다
#하루(분) % 현재시간(분) = 나머지(분) 뒤에 원하는 시간으로 정기적으로 동작한는 스케쥴러를 등록한다
#
#현재 시간을 초로 나타냄
t = time.time()
print(t)

#현지 시간
n = datetime.datetime.now()
print(n)

#지정된 시간, 0시 15분
zero_time = datetime.time(0, 15)
print(zero_time)

def get_zero_hour():
    #하루가 시작하고 지금까지 흐른 초단위 시간
    now = time.gmtime(time.time())
    y=now.tm_year 
    m=now.tm_mon 
    d=now.tm_mday
    zero_time = datetime.datetime(y, m ,d)
    now_time = datetime.datetime.now()
    gap = now_time - zero_time
    
    print(gap.total_seconds())
    
print(get_zero_hour())
# >>> now.tm_hour, now.tm_min, now.tm_sec   # 시, 분, 초
# (8, 29, 50)
