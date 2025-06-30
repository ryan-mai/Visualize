# 24/7 Hosting Setup Guide

This guide explains how to host your Discord bot 24/7 using various platforms.

## What's New

✅ **Flask Web Server**: Added a web interface to keep the bot alive
✅ **Status Dashboard**: View bot status, uptime, and statistics at `/`
✅ **Health Endpoints**: `/health` and `/ping` for monitoring
✅ **Auto-restart**: Bot will restart automatically if it crashes

## Hosting Options

### 1. Render (Recommended - Free)

1. **Fork to GitHub**: Push your code to a GitHub repository
2. **Create Render Account**: Go to [render.com](https://render.com)
3. **Create Web Service**:
   - Connect your GitHub repo
   - Choose "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python discord_bot.py`
4. **Environment Variables**:
   - Add `DISCORD_BOT_TOKEN=your_token_here`
5. **Deploy**: Your bot will be live at `https://yourapp.onrender.com`

### 2. Railway (Easy Setup)

1. **Connect GitHub**: Go to [railway.app](https://railway.app)
2. **Deploy from GitHub**: Select your repository
3. **Add Environment Variable**: `DISCORD_BOT_TOKEN=your_token_here`
4. **Deploy**: Railway handles the rest automatically

### 3. Heroku (Paid)

1. **Install Heroku CLI**: Download from [heroku.com](https://heroku.com)
2. **Create App**:
   ```bash
   heroku create your-bot-name
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   git push heroku main
   ```
3. **Scale Worker**: `heroku ps:scale web=1`

### 4. Replit (Quick Test)

1. **Import Repository**: Go to [replit.com](https://replit.com)
2. **Add Environment Variable**: `DISCORD_BOT_TOKEN` in Secrets
3. **Run**: The bot will start automatically
4. **Keep Alive**: Use UptimeRobot to ping your repl URL

## Environment Variables Required

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
PORT=5000  # Optional - for custom port
```

## Monitoring

Once deployed, you can:

- **View Status**: Visit your app URL to see the dashboard
- **Check Health**: `GET /health` returns JSON status
- **Ping Test**: `GET /ping` returns "pong"
- **API Status**: `GET /api/status` returns detailed bot info

## Features

### Web Dashboard
- Real-time bot status
- Uptime tracking
- Server count
- Command usage statistics
- Beautiful responsive design

### Bot Commands
- `/upload` - Upload 3D mesh files
- `/crinkle` - Apply noise effects
- `/dot` - Point cloud conversion
- `/poly` - Mesh simplification
- `/info` - Bot information

### Keep-Alive System
- Flask web server keeps the bot process alive
- Automatic restart on crashes
- Health monitoring endpoints
- Status reporting

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
set DISCORD_BOT_TOKEN=your_token_here  # Windows
export DISCORD_BOT_TOKEN=your_token_here  # Linux/Mac

# Run the bot
python discord_bot.py
```

Visit `http://localhost:5000` to see the status dashboard.

## Troubleshooting

### Bot Not Starting
- Check your Discord bot token is correct
- Ensure the bot has proper permissions in your Discord server
- Check the logs for specific error messages

### Web Interface Not Loading
- Verify the PORT environment variable is set correctly
- Check if the hosting platform supports web services
- Ensure Flask is installed in requirements.txt

### Commands Not Working
- Make sure slash commands are synced (check bot logs)
- Verify bot has "Use Slash Commands" permission
- Try re-inviting the bot with updated permissions

## Support

If you encounter issues:
1. Check the web dashboard for error messages
2. Review the hosting platform logs
3. Ensure all environment variables are set correctly
4. Verify the bot token and permissions

Your bot should now run 24/7 with automatic restarts and a beautiful web dashboard! 🚀
