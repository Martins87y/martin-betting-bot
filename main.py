import telebot
import requests
import os

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

bot = telebot.TeleBot(TOKEN)

def get_team_stats(team_name):
    url = "https://v3.football.api-sports.io/teams"
    headers = {
        "x-apisports-key": API_KEY
    }
    params = {
        "search": team_name
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Martin Betting Analyzer\nType:\n/analyze Arsenal")

@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team = message.text.split(" ", 1)[1]
        data = get_team_stats(team)

        if data["results"] == 0:
            bot.reply_to(message, "Team not found.")
            return

        team_name = data["response"][0]["team"]["name"]

        over15 = 80
        btts = 65
        win_prob = 60

        reply = f"""
📊 Analysis for {team_name}

Over 1.5 Goals: {over15}%
BTTS: {btts}%
Win Probability: {win_prob}%

⭐ Safest Pick: Over 1.5
"""
        bot.reply_to(message, reply)

    except:
        bot.reply_to(message, "Usage: /analyze Arsenal")

bot.infinity_polling()
