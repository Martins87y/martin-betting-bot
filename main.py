import telebot
import random
import os

# ------------------ ENV VARIABLES ------------------
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing in Railway variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------ START & PING ------------------

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
       # ------------------ START POLLING ------------------
bot.infinity_polling()
