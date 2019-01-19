### 프로그램 개요
트레이딩뷰의 얼러트를 메일로 수신하여, 거래소 API를 통해 자동매매를 실현함.


### 요구사항
Python 3.6.7이상



### 설치목록

~~~
pip install pybithumb pandas
pip install python-telegram-bot
~~~



### config 파일 생성

~~~
./configs/bithumb.key
./configs/mail.key
~~~

메일지원 : 네이버 IMAP 설정 (OPT 미지원)


### 트레이딩뷰 얼러트 설정

~~~
#BTCKRW #1M #SELL #BITHUMB
#종목심볼 #봉 #BUY/SELL타입 #거래소
~~~
얼러트 내용부분을 위의 형태로 적용.


### 실행

~~~
python ./ants/ants.py
~~~



### 주의사항

> 해당 프로그램으로 직접 투자시 위험부담은 투자자 본인에게 있습니다.
