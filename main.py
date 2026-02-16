import telebot
import requests
import os

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

bot = telebot.TeleBot(TOKEN)


def get_team_id(team_name):
    url = "https://v3.football.api-sports.io/teams"
    headers = {
        "x-apisports-key": API_KEY
    }
    params = {
        "search": team_name
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["results"] == 0:
        return None

    return data["response"][0]["team"]["id"]


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Martin Betting Analyzer\n\nUse:\n/analyze Arsenal FC")


@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team = message.text.split(" ", 1)[1]
        team_id = get_team_id(team)

        if not team_id:
            bot.reply_to(message, "❌ Team not found. Try full name like 'Arsenal FC'")
            return

        bot.reply_to(message, f"✅ Team found!\nTeam ID: {team_id}\n\nAnalysis engine upgrading...")

    except:
        bot.reply_to(message, "Usage: /analyze Arsenal FC")


bot.infinity_polling()
