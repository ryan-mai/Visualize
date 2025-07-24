from flask import Flask
import threading
import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "YEA YEAH!"

def run_discord_bot():
    bot.main()

if __name__ == "__main__":
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.daemon = True
    discord_thread.start()
    app.run(host="0.0.0.0", port=5000)
