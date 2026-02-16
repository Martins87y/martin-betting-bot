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
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        # Get the team name after the command
        team_name = message.text.split(" ", 1)[1]
        
        # Safe API call
        url = "https://v3.football.api-sports.io/teams"
        headers = {"x-apisports-key": API_KEY}
        params = {"search": team_name}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # Check if team exists
        if data["results"] == 0:
            bot.reply_to(message, "❌ Team not found. Try full name like 'Arsenal FC'")
            return

        team_info = data["response"][0]["team"]
        team_id = team_info["id"]
        team_name_correct = team_info["name"]

        # Temporary analysis (safe placeholders)
        over15 = 80
        btts = 65
        win_prob = 60

        reply = f"""
📊 Analysis for {team_name_correct} (ID: {team_id})

Over 1.5 Goals: {over15}%
BTTS: {btts}%
Win Probability: {win_prob}%

⭐ Safest Pick: Over 1.5
"""
        bot.reply_to(message, reply)

    except IndexError:
        bot.reply_to(message, "Usage: /analyze Arsenal FC")
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")
bot.infinity_polling()
