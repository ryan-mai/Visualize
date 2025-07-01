from flask import Flask, render_template, jsonify
import threading
import os
import time
from datetime import datetime

app = Flask(__name__)

# Store bot status
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
    """Main status page"""
    return render_template("index.html", status=bot_status)

@app.route('/api/status')
def api_status():
    """API endpoint for status updates"""
    # Calculate uptime
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
        uptime_str = f"{days}d {hours}h"
    
    bot_status['uptime'] = uptime_str
    return jsonify(bot_status)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring services"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': bot_status['status']
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return 'pong'

def update_bot_status(status, activity=None, guilds=None):
    """Update bot status from the Discord bot"""
    bot_status['status'] = status
    if activity:
        bot_status['last_activity'] = activity
    if guilds is not None:
        bot_status['guilds'] = guilds
    print(f"[WEB] Bot status updated: {status}")

def increment_command_count():
    """Increment the command counter"""
    bot_status['commands_processed'] += 1
    print(f"[WEB] Command count incremented to: {bot_status['commands_processed']}")

def run_flask():
    """Run Flask server in a separate thread"""
    print("[WEB] Starting Flask web server...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

def start_web_server():
    """Start the web server in a background thread"""
    web_thread = threading.Thread(target=run_flask, daemon=True)
    web_thread.start()
    print("[WEB] Web server started on port", os.environ.get('PORT', 5000))
    return web_thread

if __name__ == '__main__':
    # Run Flask server directly if this file is executed
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

