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

# ------------------ ANALYZE COMMAND ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team_name = message.text.split(" ", 1)[1]

        # Step 1: Get Team ID
        url_team = "https://v3.football.api-sports.io/teams"
        headers = {"x-apisports-key": API_KEY}
        params_team = {"search": team_name}
        response_team = requests.get(url_team, headers=headers, params=params_team)
        data_team = response_team.json()

        if data_team["results"] == 0:
            bot.reply_to(message, "❌ Team not found. Try full name like 'Arsenal FC'")
            return

        team_info = data_team["response"][0]["team"]
        team_id = team_info["id"]
        team_name_correct = team_info["name"]

        # Step 2: Get last 5 fixtures
        url_fixtures = "https://v3.football.api-sports.io/fixtures"
        params_fixtures = {"team": team_id, "last": 5}
        response_fixtures = requests.get(url_fixtures, headers=headers, params=params_fixtures)
        data_fixtures = response_fixtures.json()

        if data_fixtures["results"] == 0:
            bot.reply_to(message, f"No recent matches found for {team_name_correct}")
            return

        last_matches = data_fixtures["response"]

        # Step 3: Calculate probabilities
        over15_count = 0
        over25_count = 0
        btts_count = 0
        wins = 0

        for match in last_matches:
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            # Over 1.5 / 2.5
            if home_goals + away_goals > 1.5:
                over15_count += 1
            if home_goals + away_goals > 2.5:
                over25_count += 1

            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts_count += 1

            # Win calculation
            team_is_home = match["teams"]["home"]["id"] == team_id
            if team_is_home and home_goals > away_goals:
                wins += 1
            elif not team_is_home and away_goals > home_goals:
                wins += 1

        total = len(last_matches)
        over15_prob = round((over15_count / total) * 100)
        over25_prob = round((over25_count / total) * 100)
        btts_prob = round((btts_count / total) * 100)
        win_prob = round((wins / total) * 100)

        # Step 4: Build reply
        reply = f"""
📊 Analysis for {team_name_correct} (Last {total} matches)

Over 1.5 Goals: {over15_prob}%
Over 2.5 Goals: {over25_prob}%
BTTS: {btts_prob}%
Win Probability: {win_prob}%

⭐ Safest Pick: {'Over 1.5' if over15_prob >= 70 else 'Check BTTS / Win'}
"""
        bot.reply_to(message, reply)

    except IndexError:
        bot.reply_to(message, "Usage: /analyze <team name>")
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
