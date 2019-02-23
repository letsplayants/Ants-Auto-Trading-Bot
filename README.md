### 프로그램 개요
다양한 전략을 작성하여 전략에 맞춰 자동매매를 수행하는 것이 목표입니다
지원되는 전략
1. 트레이딩뷰의 얼러트를 메일로 수신하여, 거래소 API를 통해 자동매매를 실현함.


### 요구사항
Python 3.6.7



### 설치목록

~~~
pip install ccxt pycryptodome SQLAlchemy websocket python-telegram-bot
~~~



### config 파일 생성
configs폴더에 'sample_'로 시작하는 샘플 파일이 있습니다.
해당 샘플 파일을 아래와 같이 수정하여 사용하시면 됩니다

#### Ants config
프로그램 동작에 관여하는 설정. RSA키와 어떤 전략을 사용할지 결정합니다.
~~~
./configs/ants.conf
~~~
RSA키를 설정하는 방법은 다양한데 pem포멧 RSA만 지원합니다
윈도우 10의 경우 ssh-keygen을 사용하시면 됩니다
윈도우 7의 경우 git-bash를 받으신 후 ssh-keygen을 사용하시면됩니다. 이 때 private key 포멧을 pem으로 지정해주셔야 동작합니다.
우분투 18.04의 경우 ssh-keygen(?)으로 생성하시면 됩니다.

#### Mail config
메일을 사용하는 전략일 경우 imap에 관한 설정을 합니다.
~~~
./configs/mail.key
~~~
메일지원 : 네이버 IMAP 설정 (OTP 미지원)

#### Exchange config
거래소 지정파일은 자동으로 생성됩니다. 자동 생성을 위해서는 아래의 프로그램을 사용하여야합니다.
키 입력 후 test가 pass하지 않으면 설정이 잘못된 것입니다.
~~~
python exchange/crypt_cli.py [add/test] [exchange name]
~~~

ex) upbit key 추가
~~~
$ python exchange/crypt_cli.py add upbit
input key :
secret key :
config file save done
exchange connection test with key
test pass
~~~

ex) python bithumb key 추가
~~~
$ exchange/crypt_cli.py add bithumb
~~~

ex) python binance key 추가
~~~
$ exchange/crypt_cli.py add bithumb
~~~

ex) upbit key 연결 테스트
~~~
$ python exchange/crypt_cli.py test upbit
exchange connection test with key
test pass
~~~


### 트레이딩뷰 얼러트 설정

~~~
#BTC/KRW #1M #SELL #BITHUMB
#종목심볼/마켓 #봉 #BUY/SELL타입 #거래소
~~~
얼러트 내용부분을 위의 형태로 적용.


### 실행

~~~
python ./ants/ants.py
~~~

### 보고서
프로그램이 실행되면 data.db라는 파일이 생성됩니다. 이 파일은 sqlite3로 만들어져있으며, 매매 기록을 저장하고 있습니다.
아래의 프로그램을 사용하여 매매기록을 .csv파일을 생성합니다. 이 파일은 엑셀에서 열어볼 수 있습니다.
파일은 자동으로 생성 날짜를 붙여서 생성하므로 파일이 겹치는 일이 없습니다. 다만 프로그램이 설치될 때부터 모든 기록을 가지고 있습니다.
기록을 초기화 시키고 싶으시면 data.db파일을 지우시면 됩니다.

~~~
python exchange/csvout.py trading
~~~


### LOG
logs폴더에 ants.log가 출력됩니다. 현재 개발버젼이라 debug 메시지도 함께 출력이 되어 log가 꽤 크게 남습니다.
이를 변경하려면 configs/log.conf 파일에 DEBUG부분을 INFO로 변경하시면 됩니다. 이 부분은 배포 버젼에서 INFO로 변경될 것입니다


### 지원거래소

#### 업비트
#### 빗썸
#### 바이낸스


### 주의사항

> 해당 프로그램으로 직접 투자시 위험부담은 투자자 본인에게 있습니다.
