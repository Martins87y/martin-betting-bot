import telebot
import requests
import os

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

if not TOKEN:
    raise ValueError("TOKEN is missing in Railway variables.")

if not API_KEY:
    raise ValueError("API_KEY is missing in Railway variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------ START COMMAND ------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🔥 Martin Betting Analyzer\n\nUse /ping to check bot\nUse /analyze <team name>"
    )

# ------------------ PING COMMAND ------------------
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ TOP TEAMS DATA (Free Plan) ------------------
# league = 39 (Premier League), season = 2026
teams = {
    "Arsenal FC": {"id": 42, "league": 39, "season": 2026},
    "Chelsea FC": {"id": 49, "league": 39, "season": 2026},
    "Liverpool FC": {"id": 40, "league": 39, "season": 2026},
    "Manchester United FC": {"id": 33, "league": 39, "season": 2026},
    "Manchester City FC": {"id": 50, "league": 39, "season": 2026},
    "Tottenham Hotspur FC": {"id": 47, "league": 39, "season": 2026}
}

# ------------------ ANALYZE COMMAND ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team_name = message.text.split(" ", 1)[1]

        # Check if team exists in predefined list
        if team_name not in teams:
            bot.reply_to(message, "❌ Team not found in top Premier League teams.")
            return

        team_info = teams[team_name]
        team_id = team_info["id"]
        league_id = team_info["league"]
        season = team_info["season"]

        # ------------------ GET LAST 5 MATCHES ------------------
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            "x-apisports-key": API_KEY,
            "Accept": "application/json"
        }
        params = {
            "team": team_id,
            "league": league_id,
            "season": season,
            "last": 5
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data["results"] == 0:
            bot.reply_to(message, f"No recent matches found for {team_name}")
            return

        matches = data["response"]

        # ------------------ CALCULATE PROBABILITIES ------------------
        over15 = 0
        over25 = 0
        btts = 0
        wins = 0

        for match in matches:
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            # Over 1.5 / 2.5
            if home_goals + away_goals > 1.5:
                over15 += 1
            if home_goals + away_goals > 2.5:
                over25 += 1

            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts += 1

            # Win calculation
            team_is_home = match["teams"]["home"]["id"] == team_id
            if team_is_home and home_goals > away_goals:
                wins += 1
            elif not team_is_home and away_goals > home_goals:
                wins += 1

        total = len(matches)
        over15_prob = round((over15 / total) * 100)
        over25_prob = round((over25 / total) * 100)
        btts_prob = round((btts / total) * 100)
        win_prob = round((wins / total) * 100)

        # ------------------ BUILD REPLY ------------------
        safest_pick = "Over 1.5" if over15_prob >= 70 else "Check BTTS / Win"

        reply = f"""
📊 Analysis for {team_name} (Last {total} matches)

Over 1.5 Goals: {over15_prob}%
Over 2.5 Goals: {over25_prob}%
BTTS: {btts_prob}%
Win Probability: {win_prob}%

⭐ Safest Pick: {safest_pick}
"""
        bot.reply_to(message, reply)

    except IndexError:
        bot.reply_to(message, "Usage: /analyze <team name>")
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
