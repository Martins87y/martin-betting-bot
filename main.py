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
        "🔥 Martin Betting Analyzer (Advanced Multi-League)\n\n"
        "Commands:\n"
        "/ping - Check if bot is alive\n"
        "/analyze <team1>; <team2>; ... - Multi-team analysis\n"
        "/daily - Top safest picks per league today"
    )

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ LEAGUES & TEAMS ------------------
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

# Flatten for validation
all_teams = [t for t_list in leagues.values() for t in t_list]

# ------------------ ANALYZE MULTI-TEAM COMMAND ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        raw_text = message.text.split(" ", 1)
        if len(raw_text) < 2:
            bot.reply_to(message, "Usage: /analyze <team1>; <team2>; ...")
            return

        teams_input = [t.strip() for t in raw_text[1].split(";")]
        results = []

        for team_name in teams_input:
            if team_name not in all_teams:
                results.append({"team": team_name, "error": "❌ Team not found"})
                continue

            # Simulate last 5 matches
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

            # Calculate probabilities
            over15 = over25 = btts = wins = 0
            for match in matches:
                home = match["home_goals"]
                away = match["away_goals"]
                total_goals = home + away

                if total_goals > 1.5: over15 += 1
                if total_goals > 2.5: over25 += 1
                if home > 0 and away > 0: btts += 1
                if match["team_is_home"] and home > away: wins += 1
                elif not match["team_is_home"] and away > home: wins += 1

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

        # Build reply
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

        bot.reply_to(message, "\n".join(reply_lines))

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ DAILY SAFEST PICKS ------------------
@bot.message_handler(commands=['daily'])
def daily(message):
    try:
        reply_lines = []
        for league_name, teams_list in leagues.items():
            league_results = []

            for team_name in teams_list:
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

                over15 = sum(1 for m in matches if m["home_goals"] + m["away_goals"] > 1.5)
                safest_pick = "Over 1.5" if over15 >= 4 else "Check BTTS / Win"
                league_results.append({
                    "team": team_name,
                    "over15": round((over15 / 5) * 100),
                    "safest": safest_pick
                })

            # Rank by over15 probability
            league_results.sort(key=lambda x: x["over15"], reverse=True)
            top = league_results[0]
            reply_lines.append(f"🏆 {league_name} Top Pick: {top['team']} ({top['safest']})")

        bot.reply_to(message, "\n".join(reply_lines))

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
