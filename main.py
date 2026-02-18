import telebot
import random
import os

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN is missing in Railway variables.")

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

# ------------------ TOP TEAMS ------------------
# You can expand this list later for other leagues
teams = [
    "Arsenal FC", "Chelsea FC", "Liverpool FC",
    "Manchester United FC", "Manchester City FC",
    "Tottenham Hotspur FC", "Leicester City FC", "Everton FC"
]

# ------------------ ANALYZE COMMAND ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team_name = message.text.split(" ", 1)[1]

        # Check if team exists in our list
        if team_name not in teams:
            bot.reply_to(message, "❌ Team not found in top Premier League teams.")
            return

        # ------------------ SIMULATE LAST 5 MATCHES ------------------
        matches = []
        for _ in range(5):
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 4)
            team_is_home = random.choice([True, False])
            matches.append({
                "home_goals": home_goals,
                "away_goals": away_goals,
                "team_is_home": team_is_home
            })

        # ------------------ CALCULATE PROBABILITIES ------------------
        over15 = over25 = btts = wins = 0

        for match in matches:
            home = match["home_goals"]
            away = match["away_goals"]
            total_goals = home + away

            if total_goals > 1.5:
                over15 += 1
            if total_goals > 2.5:
                over25 += 1
            if home > 0 and away > 0:
                btts += 1

            if match["team_is_home"] and home > away:
                wins += 1
            elif not match["team_is_home"] and away > home:
                wins += 1

        total = len(matches)
        over15_prob = round((over15 / total) * 100)
        over25_prob = round((over25 / total) * 100)
        btts_prob = round((btts / total) * 100)
        win_prob = round((wins / total) * 100)

        # ------------------ SAFEST PICK ------------------
        safest_pick = "Over 1.5" if over15_prob >= 70 else "Check BTTS / Win"

        # ------------------ BUILD REPLY ------------------
        reply = f"""
📊 Analysis for {team_name} (Simulated Last {total} Matches)

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
