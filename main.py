import telebot
import requests
import os

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

if not TOKEN:
    raise ValueError("TOKEN is missing. Check Railway variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------ START COMMAND ------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Martin Betting Analyzer\nUse /ping to check bot")

# ------------------ PING COMMAND ------------------
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team_name = message.text.split(" ", 1)[1]

        url = "https://v3.football.api-sports.io/teams"
        headers = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
        params = {"search": team_name}

        response = requests.get(url, headers=headers, params=params)

        bot.reply_to(message, f"Status Code: {response.status_code}\nResponse: {response.text[:500]}")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
bot.infinity_polling()
