import telebot
import requests
import os
from datetime import datetime, timedelta

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")  # Your Football-Data.org API key

if not TOKEN:
    raise ValueError("TOKEN is missing in Railway variables.")

if not API_KEY:
    raise ValueError("API_KEY is missing in Railway variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------ START & PING ------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🔥 Martin Real Analyzer\n\n"
        "Commands:\n"
        "/ping - Check if bot is alive\n"
        "/analyze <team name> - Get real stats for team\n"
        "/daily - Top safest picks per league (simulated)"
    )

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ TOP TEAMS WITH Football-Data IDs ------------------
# Premier League example: add more leagues and teams as needed
teams = {
    "Arsenal FC": 57,
    "Chelsea FC": 61,
    "Liverpool FC": 64,
    "Manchester United FC": 66,
    "Manchester City FC": 65,
    "Tottenham Hotspur FC": 73
}

BASE_URL = "https://api.football-data.org/v4"

# ------------------ ANALYZE REAL TEAM ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        raw_text = message.text.split(" ", 1)
        if len(raw_text) < 2:
            bot.reply_to(message, "Usage: /analyze <team name>")
            return

        team_name = raw_text[1].strip()
        if team_name not in teams:
            bot.reply_to(message, "❌ Team not found in supported teams")
            return

        team_id = teams[team_name]

        # ------------------ Fetch Last 10 Finished Matches ------------------
        headers = {"X-Auth-Token": API_KEY}
        url = f"{BASE_URL}/teams/{team_id}/matches?status=FINISHED&limit=10"
        response = requests.get(url, headers=headers)
        data = response.json()

        matches = data.get("matches", [])

        if not matches:
            bot.reply_to(message, f"No recent matches found for {team_name}")
            return

        # ------------------ Calculate Probabilities ------------------
        over15 = over25 = btts = wins = 0
        for match in matches:
            home = match["score"]["fullTime"]["home"]
            away = match["score"]["fullTime"]["away"]

            if home is None or away is None:
                continue

            total_goals = home + away

            if total_goals > 1.5: over15 += 1
            if total_goals > 2.5: over25 += 1
            if home > 0 and away > 0: btts += 1

            team_is_home = match["home"]["id"] == team_id
            if (team_is_home and home > away) or (not team_is_home and away > home):
                wins += 1

        total = len(matches)
        over15_prob = round((over15 / total) * 100)
        over25_prob = round((over25 / total) * 100)
        btts_prob = round((btts / total) * 100)
        win_prob = round((wins / total) * 100)

        safest_pick = "Over 1.5" if over15_prob >= 70 else "Check BTTS / Win"

        # ------------------ Build Reply ------------------
        reply = f"""
📊 Real Analysis for {team_name} (Last {total} Matches)

Over 1.5 Goals: {over15_prob}%
Over 2.5 Goals: {over25_prob}%
BTTS: {btts_prob}%
Win Probability: {win_prob}%

⭐ Safest Pick: {safest_pick}
"""
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ DAILY SAFEST PICKS (Simulated for now) ------------------
@bot.message_handler(commands=['daily'])
def daily(message):
    reply_lines = [
        "🏆 Daily Safest Picks (Simulated):",
        "Premier League: Arsenal FC - Over 1.5",
        "La Liga: Barcelona - Over 1.5",
        "Serie A: Juventus - Over 1.5",
        "Bundesliga: Bayern Munich - Over 1.5",
        "Ligue 1: Paris SG - Over 1.5"
    ]
    bot.reply_to(message, "\n".join(reply_lines))

# ------------------ START BOT ------------------
bot.infinity_polling()
