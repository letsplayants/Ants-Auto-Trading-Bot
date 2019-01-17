#Telegram에서 수신된 메시지를 파싱한다

import telegram
from read_api_key import readKey

mtoken = readKey('telegram_bot.key')
bot = telegram.Bot(token=mtoken["bot_token"])

print(bot.get_me())

#메시지 읽어옴
for message in bot.getUpdates() :
    print(message)

bot.sendMessage(chat_id = -241706808, text="저는 봇입니다.")

#지정된 봇 이외의 대화는 다 차단한다
