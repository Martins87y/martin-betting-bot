import telebot
import random
import os

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing in Railway variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------ START & PING ------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🔥 Martin Betting Analyzer (Advanced)\n\n"
        "Use /ping to check bot\n"
        "Use /analyze <team1>; <team2>; <team3> ...")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ MULTI-LEAGUE TEAM DATA ------------------
# Add more teams or leagues as needed
leagues = {
    "Premier League": [
        "Arsenal FC", "Chelsea FC", "Liverpool FC",
        "Manchester United FC", "Manchester City FC",
        "Tottenham Hotspur FC", "Leicester City FC", "Everton FC"
    ],
    "La Liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid",
        "Sevilla", "Valencia"
    ],
    "Serie A": [
        "Juventus", "AC Milan", "Inter Milan",
        "Napoli", "Roma"
    ],
    "Bundesliga": [
        "Bayern Munich", "Borussia Dortmund",
        "RB Leipzig", "Bayer Leverkusen"
    ],
    "Ligue 1": [
        "Paris SG", "Marseille", "Monaco",
        "Lyon", "Nice"
    ]
}

# Flatten all teams for validation
all_teams = []
for t_list in leagues.values():
    all_teams += t_list

# ------------------ ANALYZE COMMAND ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        # Split multiple teams by semicolon
        raw_text = message.text.split(" ", 1)
        if len(raw_text) < 2:
            bot.reply_to(message, "Usage: /analyze <team1>; <team2>; ...")
            return

        teams_input = [t.strip() for t in raw_text[1].split(";")]
        results = []

        for team_name in teams_input:
            if team_name not in all_teams:
                results.append({
                    "team": team_name,
                    "error": "❌ Team not found in supported leagues"
                })
                continue

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

                if total_goals > 1.5: over15 += 1
                if total_goals > 2.5: over25 += 1
                if home > 0 and away > 0: btts += 1

                if match["team_is_home"] and home > away:
                    wins += 1
                elif not match["team_is_home"] and away > home:
                    wins += 1

            total = len(matches)
            over15_prob = round((over15 / total) * 100)
            over25_prob = round((over25 / total) * 100)
            btts_prob = round((btts / total) * 100)
            win_prob = round((wins / total) * 100)

            safest_pick = "Over 1.5" if over15_prob >= 70 else "Check BTTS / Win"

            results.append({
                "team": team_name,
                "over15": over15_prob,
                "over25": over25_prob,
                "btts": btts_prob,
                "win": win_prob,
                "safest": safest_pick
            })

        # ------------------ BUILD TELEGRAM REPLY ------------------
        reply_lines = []
        for r in results:
            if "error" in r:
                reply_lines.append(f"{r['team']}: {r['error']}")
            else:
                reply_lines.append(
                    f"📊 {r['team']}\n"
                    f"Over 1.5: {r['over15']}% | Over 2.5: {r['over25']}% | "
                    f"BTTS: {r['btts']}% | Win: {r['win']}%\n"
                    f"⭐ Safest Pick: {r['safest']}\n"
                )

        # Rank teams by Over 1.5 probability (or other logic if needed)
        ranked = [r for r in results if "error" not in r]
        ranked.sort(key=lambda x: x["over15"], reverse=True)
        if ranked:
            top_team = ranked[0]
            reply_lines.append(f"🏆 Top Safest Pick Today: {top_team['team']} ({top_team['safest']})")

        bot.reply_to(message, "\n".join(reply_lines))

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
