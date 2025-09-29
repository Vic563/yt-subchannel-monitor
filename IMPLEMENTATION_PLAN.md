# YouTube Subscription Monitor - Implementation Plan

## 🎯 Project Overview
A GitHub Actions-based application that monitors YouTube subscriptions and sends Telegram notifications for new videos.

## 🏗️ Architecture Components

### 1. YouTube API Integration
**Purpose**: Fetch user subscriptions and check for new videos

**Implementation Details**:
- Use YouTube Data API v3
- OAuth2 authentication for accessing private user data
- Required scopes: `youtube.readonly`
- API calls needed:
  - `subscriptions.list` - Get user's subscriptions
  - `channels.list` - Get channel details
  - `search.list` or `activities.list` - Get recent videos

**Challenges & Solutions**:
- **Challenge**: OAuth2 tokens expire
- **Solution**: Store refresh token as GitHub secret, refresh access token on each run

### 2. Telegram Bot Integration
**Purpose**: Send notifications about new videos

**Message Format**:
```
🎬 New Video Alert!
Channel: {{channel_name}}
Title: {{video_title}}
Link: https://youtube.com/watch?v={{video_id}}
Posted: {{time_ago}}
```

**Implementation**:
- Create bot via @BotFather
- Use python-telegram-bot library
- Send rich messages with video thumbnails

### 3. State Management
**Purpose**: Track which videos have been notified to avoid duplicates

**State File Structure** (`data/state.json`):
```json
{
  "channels": {
    "CHANNEL_ID_1": {
      "name": "Channel Name",
      "latest_video_id": "VIDEO_ID",
      "latest_video_timestamp": "2024-01-01T00:00:00Z",
      "last_checked": "2024-01-01T00:00:00Z"
    }
  },
  "metadata": {
    "last_run": "2024-01-01T00:00:00Z",
    "total_notifications_sent": 0
  }
}
```

### 4. GitHub Actions Workflow

**Schedule Options**:
- Every 15 minutes: `*/15 * * * *` (96 runs/day)
- Every 30 minutes: `*/30 * * * *` (48 runs/day)
- Every hour: `0 * * * *` (24 runs/day)

**Workflow Features**:
- Automatic retries on failure
- Error notifications
- Rate limit handling
- Execution time limits

## 📝 Setup Instructions

### Step 1: YouTube API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth2 credentials (Desktop application type)
5. Download credentials JSON

### Step 2: Telegram Bot Setup
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Save the bot token
4. Get your chat ID (message @userinfobot)

### Step 3: GitHub Repository Setup
1. Fork/create repository
2. Add secrets in Settings > Secrets:
   - `YOUTUBE_API_KEY`
   - `YOUTUBE_REFRESH_TOKEN`
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### Step 4: Initial OAuth2 Authentication
Run locally once to get refresh token:
```bash
python setup_oauth.py
```

## 🚀 Implementation Phases

### Phase 1: Basic Functionality (MVP)
- [x] Project structure setup
- [ ] YouTube API client with OAuth2
- [ ] Telegram bot client
- [ ] Basic state management
- [ ] Simple GitHub Actions workflow

### Phase 2: Enhanced Features
- [ ] Rich Telegram messages with thumbnails
- [ ] Multiple user support
- [ ] Channel filtering/exclusion
- [ ] Notification scheduling (quiet hours)

### Phase 3: Advanced Features
- [ ] Web dashboard for configuration
- [ ] Statistics and analytics
- [ ] Webhook support
- [ ] Email notifications option

## 🔒 Security Considerations

1. **API Keys**: All sensitive data stored as GitHub secrets
2. **State File**: No sensitive data in state.json
3. **Rate Limiting**: Implement exponential backoff
4. **Token Refresh**: Automatic token refresh handling

## 📊 Monitoring & Debugging

1. **Logs**: GitHub Actions logs for each run
2. **Error Handling**: Graceful failures with descriptive messages
3. **Test Mode**: Dry-run option without sending notifications
4. **Health Checks**: Optional webhook for monitoring uptime

## 🎯 Success Metrics

- Notification delivery within 30 minutes of video upload
- 99%+ uptime (considering GitHub Actions limits)
- Zero duplicate notifications
- Minimal API quota usage

## 🚧 Known Limitations

1. **GitHub Actions Limits**:
   - 2,000 minutes/month (free tier)
   - 6-hour maximum workflow duration
   - 1,000 API requests per hour

2. **YouTube API Quotas**:
   - 10,000 units per day
   - Each API call costs different units

3. **Delay Considerations**:
   - Minimum 15-minute delay (cron schedule)
   - API caching may add 5-10 minutes

## 🔄 Future Enhancements

1. Support for YouTube premieres
2. Live stream notifications
3. Community post notifications
4. Multi-language support
5. Custom notification templates
