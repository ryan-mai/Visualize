from flask import Flask, render_template, jsonify
import threading
import os
from datetime import datetime

app = Flask(__name__)

bot_status = {
    'status': 'Starting...',
    'start_time': datetime.now(),
    'uptime': '0 seconds',
    'commands_processed': 0,
    'guilds': 0,
    'last_activity': 'Bot starting up...'
}

@app.route('/')
def home():
    return render_template("index.html", status=bot_status)

@app.route('/api/status')
def api_status():
    uptime_seconds = (datetime.now() - bot_status['start_time']).total_seconds()
    if uptime_seconds < 60:
        uptime_str = f"{int(uptime_seconds)} seconds"
    elif uptime_seconds < 3600:
        uptime_str = f"{int(uptime_seconds // 60)} minutes"
    elif uptime_seconds < 86400:
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{hours}h {minutes}m"
    else:
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        uptime_str = f"{days}d {hours}
        
    bot_status['uptime'] = uptime_str
    return jsonify(bot_status)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': bot_status['status']
    })

@app.route('/ping')
def ping():
    return 'pong'

def update_bot_status(status, activity=None, guilds=None):
    bot_status['status'] = status
    if activity:
        bot_status['last_activity'] = activity
    if guilds is not None:
        bot_status['guilds'] = guilds

def increment_command_count():
    bot_status['commands_processed'] += 1
    print(f"[WEB] Command count incremented to: {bot_status['commands_processed']}")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

def start_web_server():
    web_thread = threading.Thread(target=run_flask, daemon=True)
    web_thread.start()
    print("[WEB] Web server started on port", os.environ.get('PORT', 5000))
    return web_thread

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
