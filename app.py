from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord Bot - Online</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .status { color: #28a745; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1>Discord Bot Status</h1>
        <p class="status">🟢 Online</p>
        <p>Bot is running and ready to process commands.</p>
    </body>
    </html>
    '''

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/health')
def health():
    return 'ok'

def run_flask():
    print("[WEB] Starting simple Flask server for uptime monitoring...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

def start_web_server():
    web_thread = threading.Thread(target=run_flask, daemon=True)
    web_thread.start()
    print(f"[WEB] Web server started on port {os.environ.get('PORT', 5000)}")
    return web_thread

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

