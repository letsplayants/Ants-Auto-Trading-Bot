import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

bot_token = ""
chat_id = ""

    
bot = telegram.Bot(token=bot_token)

print(bot.first_name)
print(bot.get_me())
print(bot.get_me()['username'])