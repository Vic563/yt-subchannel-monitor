# 🎬 YouTube Subscription Monitor

A GitHub Actions-powered bot that monitors your YouTube subscriptions and sends Telegram notifications when new videos are posted. Runs entirely on GitHub's infrastructure with no external servers required!

## ✨ Features

- 📺 **Automatic Monitoring**: Checks your YouTube subscriptions every 30 minutes
- 💬 **Telegram Notifications**: Instant alerts when your favorite creators upload
- 🔄 **Stateful Tracking**: Never sends duplicate notifications
- 🚀 **Serverless**: Runs entirely on GitHub Actions - no hosting required
- 🔐 **Secure**: All credentials stored as GitHub Secrets
- ⚡ **Efficient**: Smart API usage to stay within quotas

## 📋 Prerequisites

Before setting up this monitor, you'll need:

1. **Google Cloud Account** (for YouTube API)
2. **Telegram Account** (for notifications)  
3. **GitHub Account** (for running the bot)

## 🛠️ Setup Guide

### Step 1: Fork This Repository

1. Click the "Fork" button at the top of this repository
2. Clone your fork locally: `git clone https://github.com/YOUR_USERNAME/yt-subchannel-monitor.git`

### Step 2: YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click and enable it

4. Create API Key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy and save the API key

5. Create OAuth2 Credentials:
   - Click "Create Credentials" > "OAuth client ID"
   - Configure consent screen if needed
   - Application type: "Desktop app"
   - Download the credentials JSON file

### Step 3: Get YouTube Refresh Token

1. Run the OAuth setup script locally:
   ```bash
   pip install -r requirements.txt
   python setup_oauth.py
   ```

2. Follow the prompts:
   - Enter path to your downloaded credentials JSON
   - Log in with your Google account
   - Authorize the app to read your YouTube subscriptions
   - Save the displayed tokens

### Step 4: Telegram Bot Setup

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Create a new bot:
   - Send `/newbot`
   - Choose a name for your bot
   - Choose a username (must end in 'bot')
   - Save the bot token

3. Get your Chat ID:
   - Message [@userinfobot](https://t.me/userinfobot)
   - Or message your bot and visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for the "chat" object and copy the "id"

### Step 5: Configure GitHub Secrets

In your forked repository, go to Settings > Secrets and variables > Actions, and add:

| Secret Name | Description |
|------------|-------------|
| `YOUTUBE_API_KEY` | Your YouTube Data API key |
| `YOUTUBE_CLIENT_ID` | OAuth2 client ID |
| `YOUTUBE_CLIENT_SECRET` | OAuth2 client secret |
| `YOUTUBE_REFRESH_TOKEN` | OAuth2 refresh token (from setup script) |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

### Step 6: Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. Run the "Setup and Test" workflow to verify everything works

## 🚀 Usage

Once configured, the bot will:
- Run automatically every 30 minutes
- Check all your YouTube subscriptions
- Send Telegram notifications for new videos
- Update the state file to track notified videos

### Manual Trigger

You can manually run the monitor:
1. Go to Actions > "YouTube Subscription Monitor"
2. Click "Run workflow"
3. Optionally enable test mode

### Notification Format

```
🎬 New Video Alert!

📺 Channel: TechChannel
📝 Title: Amazing New Tech Review
🔗 Link: https://youtube.com/watch?v=...
⏰ Posted: 2 hours ago
```

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "youtube": {
    "check_interval_minutes": 30,
    "max_results_per_channel": 5
  },
  "telegram": {
    "notification_template": "..."
  },
  "general": {
    "dry_run": false,
    "debug": false
  }
}
```

## 📊 Monitoring & Debugging

### View Logs
- Go to Actions tab
- Click on a workflow run
- View detailed logs for each step

### Check State
The `data/state.json` file tracks:
- Last checked time for each channel
- Latest notified video per channel
- Total notifications sent

### Test Mode
Run with test mode to verify connections without processing:
```bash
python src/youtube_monitor.py --test
```

## ⚠️ Limitations

### GitHub Actions
- **Free tier**: 2,000 minutes/month
- Each run uses ~1-2 minutes
- 30-minute schedule = ~48 runs/day = ~1,440 minutes/month

### YouTube API
- **Quota**: 10,000 units/day
- Typical usage: ~100-500 units per run
- Well within limits for personal use

### Delays
- Minimum 30-minute delay between checks
- YouTube API caching may add 5-10 minutes
- Total delay: 30-45 minutes from upload to notification

## 🐛 Troubleshooting

### No Notifications
1. Check Actions tab for errors
2. Verify all secrets are set correctly
3. Run Setup workflow to test connections
4. Check `state.json` for updates

### API Errors
- **401 Unauthorized**: Check credentials
- **403 Forbidden**: Check API quotas
- **Invalid grant**: Refresh token expired, run setup again

### Telegram Errors
- Verify bot token is correct
- Ensure you've messaged the bot first
- Check chat ID is correct

## 🔒 Security

- All credentials stored as GitHub Secrets
- State file contains no sensitive data
- OAuth tokens auto-refresh
- Read-only YouTube access

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 💡 Future Enhancements

- [ ] Support for multiple users
- [ ] Web dashboard for configuration
- [ ] Filter channels or keywords
- [ ] Support for live streams
- [ ] Discord/Slack notifications
- [ ] Custom notification schedules

## 🙏 Acknowledgments

- Built with [Google's YouTube Data API](https://developers.google.com/youtube/v3)
- Notifications via [Telegram Bot API](https://core.telegram.org/bots/api)
- Powered by [GitHub Actions](https://github.com/features/actions)

---

Made with ❤️ for YouTube enthusiasts who never want to miss a video!
