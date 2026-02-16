import telebot
import requests
import os

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

if not TOKEN:
    raise ValueError("TOKEN is missing. Check Railway variables.")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Martin Betting Analyzer\nUse /ping to check bot")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

bot.infinity_polling()
