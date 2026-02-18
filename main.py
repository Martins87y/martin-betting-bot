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
        "🔥 Martin Realistic Simulator Analyzer\n\n"
        "Commands:\n"
        "/ping - Check if bot is alive\n"
        "/analyze <team1>; <team2>; ... - Multi-team analysis\n"
        "/daily - Top safest picks per league"
    )

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ LEAGUES & TEAM STRENGTHS ------------------
leagues = {
    "Premier League": {
        "Arsenal FC": 1.2,
        "Chelsea FC": 1.1,
        "Liverpool FC": 1.3,
        "Manchester United FC": 1.2,
        "Manchester City FC": 1.3,
        "Tottenham Hotspur FC": 1.0,
        "Leicester City FC": 0.9,
        "Everton FC": 0.9
    },
    "La Liga": {
        "Real Madrid": 1.3,
        "Barcelona": 1.3,
        "Atletico Madrid": 1.2,
        "Sevilla": 1.0,
        "Valencia": 0.9
    },
    "Serie A": {
        "Juventus": 1.2,
        "AC Milan": 1.1,
        "Inter Milan": 1.2,
        "Napoli": 1.2,
        "Roma": 1.0
    },
    "Bundesliga": {
        "Bayern Munich": 1.3,
        "Borussia Dortmund": 1.2,
        "RB Leipzig": 1.1,
        "Bayer Leverkusen": 1.0
    },
    "Ligue 1": {
        "Paris SG": 1.3,
        "Marseille": 1.1,
        "Monaco": 1.1,
        "Lyon": 1.0,
        "Nice": 0.9
    }
}

# ------------------ FLATTEN TEAMS FOR QUICK LOOKUP ------------------
all_teams = {team: strength for league in leagues.values() for team, strength in league.items()}

# ------------------ SIMULATE MATCH ------------------
def simulate_match(team_strength):
    """Weighted goal simulation with home advantage"""
    goals_weights = [0.2, 0.35, 0.25, 0.15, 0.05]  # 0-4 goals probability
    home_goals = random.choices([0,1,2,3,4], weights=goals_weights, k=1)[0]
    away_goals = random.choices([0,1,2,3,4], weights=goals_weights, k=1)[0]

    # Apply team strength
    home_goals = min(4, int(home_goals * team_strength))
    away_goals = min(4, int(away_goals * (2 - team_strength)))  # weaker side

    # Home advantage
    if random.random() < 0.55:
        home_goals += 1
        home_goals = min(home_goals, 4)

    return home_goals, away_goals, random.choice([True, False])  # True if team is home

# ------------------ MULTI-TEAM ANALYZE ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        raw_text = message.text.split(" ",1)
        if len(raw_text)<2:
            bot.reply_to(message, "Usage: /analyze <team1>; <team2>; ...")
            return

        teams_input = [t.strip() for t in raw_text[1].split(";")]
        results = []

        for team_name in teams_input:
            if team_name not in all_teams:
                results.append({"team": team_name, "error": "❌ Team not supported"})
                continue

            strength = all_teams[team_name]

            # Simulate last 5 matches
            over15=over25=btts=wins=0
            matches_total = 5
            for _ in range(matches_total):
                home_goals, away_goals, team_is_home = simulate_match(strength)
                total_goals = home_goals + away_goals

                if total_goals>1.5: over15+=1
                if total_goals>2.5: over25+=1
                if home_goals>0 and away_goals>0: btts+=1

                if (team_is_home and home_goals>away_goals) or (not team_is_home and away_goals>home_goals):
                    wins+=1

            over15_prob = round((over15/matches_total)*100)
            over25_prob = round((over25/matches_total)*100)
            btts_prob = round((btts/matches_total)*100)
            win_prob = round((wins/matches_total)*100)

            safest_pick = "Over 1.5" if over15_prob>=70 else "Check BTTS / Win"

            results.append({
                "team": team_name,
                "over15": over15_prob,
                "over25": over25_prob,
                "btts": btts_prob,
                "win": win_prob,
                "safest": safest_pick
            })

        # Rank the input teams by Over 1.5 probability
        ranked = [r for r in results if "error" not in r]
        ranked.sort(key=lambda x: x["over15"], reverse=True)

        # Build reply
        reply_lines=[]
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

        if ranked:
            top = ranked[0]
            reply_lines.append(f"🏆 Top Safest Pick Among Selected Teams: {top['team']} ({top['safest']})")

        bot.reply_to(message, "\n".join(reply_lines))

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ DAILY SAFEST PICKS ------------------
@bot.message_handler(commands=['daily'])
def daily(message):
    try:
        all_results = []

        for league_name, teams_dict in leagues.items():
            for team, strength in teams_dict.items():
                over15 = 0
                for _ in range(5):
                    home_goals, away_goals, _ = simulate_match(strength)
                    if home_goals + away_goals > 1.5:
                        over15 += 1
                prob = round((over15 / 5) * 100)
                safest = "Over 1.5" if prob >= 70 else "Check BTTS / Win"

                all_results.append({
                    "league": league_name,
                    "team": team,
                    "over15": prob,
                    "safest": safest
                })

        # Rank all teams by Over 1.5 probability
        all_results.sort(key=lambda x: x["over15"], reverse=True)

        # Build reply
        reply_lines = ["🏆 Daily Top Safest Picks Across Leagues:"]
        for r in all_results[:10]:
            reply_lines.append(f"{r['team']} ({r['league']}) - {r['safest']} [{r['over15']}%]")

        bot.reply_to(message, "\n".join(reply_lines))

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
