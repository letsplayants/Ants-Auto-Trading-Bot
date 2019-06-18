import datetime
import pytz

ttime = datetime.datetime.now(pytz.timezone('Asia/Seoul')) 
nowDate = ttime.strftime('%Y-%m-%d %H:%M')
print(nowDate)