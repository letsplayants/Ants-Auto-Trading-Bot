import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


def get_zero_hour():
    #하루가 시작하고 지금까지 흐른 초단위 시간
    now = time.gmtime(time.time())
    y=now.tm_year 
    m=now.tm_mon 
    d=now.tm_mday
    zero_time = datetime(y, m ,d)
    return zero_time


def job_function(key):
    n = datetime.now()
    print(f'{n}\t{key}')

sched = BackgroundScheduler()


s_date = get_zero_hour()

# apscheduler.triggers.interval.IntervalTrigger(weeks=0, days=0, hours=0, minutes=0, seconds=0, start_date=None, end_date=None, timezone=None, jitter=None)
# 시작 시간이 후 지정된 인터벌마다 콜이 된다. 시작시간은 과거를 넣어도 잘 동작한다
sched.add_job(job_function, 'interval', args=['hello'], start_date=s_date, minutes=3)

available_key_list = ['1m','10m','15m','30m','45m','60m','120m','180m','240m','300m','360m','480m','720m','1440m']
for key in available_key_list:
    minute = int(key[:len(key)-1])
    sched.add_job(job_function, 'interval',args=[key], start_date=s_date, minutes=minute)
        
sched.start()

while(True):
    time.sleep(1)