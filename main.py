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
    bot.reply_to(message, "🔥 Martin Betting Analyzer\n\nUse /ping to check bot\nUse /analyze <team name>")

# ------------------ PING COMMAND ------------------
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is alive!")

# ------------------ ANALYZE (DEBUG VERSION) ------------------
@bot.message_handler(commands=['analyze'])
def analyze(message):
    try:
        team_name = message.text.split(" ", 1)[1]

        url = "https://v3.football.api-sports.io/teams"

        headers = {
            "x-apisports-key": API_KEY,
            "Accept": "application/json"
        }

        params = {
            "search": team_name
        }

        response = requests.get(url, headers=headers, params=params)

        bot.reply_to(
            message,
            f"Status Code: {response.status_code}\n\nResponse:\n{response.text[:800]}"
        )

    except IndexError:
        bot.reply_to(message, "Usage: /analyze <team name>")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ------------------ START POLLING ------------------
bot.infinity_polling()
