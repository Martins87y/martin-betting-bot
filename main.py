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


# ----------------- ADD ANALYZE COMMAND BELOW -----------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        # Get the team name from user input
        team_name = message.text.split(" ", 1)[1]

        # Temporary safe analysis (bypassing API issues)
        over15 = 80
        btts = 65
        win_prob = 60

        reply = f"""
📊 Analysis for {team_name} (Simulated Data)

Over 1.5 Goals: {over15}%
BTTS: {btts}%
Win Probability: {win_prob}%

⭐ Safest Pick: Over 1.5
"""
        bot.reply_to(message, reply)

    except IndexError:
        bot.reply_to(message, "Usage: /analyze <team name>")


bot.infinity_polling()
