"""Main YouTube subscription monitoring script."""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from youtube_client import YouTubeClient
from telegram_client import TelegramClient
from state_manager import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class YouTubeMonitor:
    """Main class for monitoring YouTube subscriptions."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the monitor.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize clients
        self.youtube_client = self._init_youtube_client()
        self.telegram_client = self._init_telegram_client()
        self.state_manager = StateManager()
        
        # Statistics
        self.stats = {
            'channels_checked': 0,
            'new_videos_found': 0,
            'notifications_sent': 0,
            'errors': 0
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _init_youtube_client(self) -> YouTubeClient:
        """Initialize YouTube client from environment variables.
        
        Returns:
            YouTubeClient instance
        """
        required_vars = [
            'YOUTUBE_CLIENT_ID',
            'YOUTUBE_CLIENT_SECRET',
            'YOUTUBE_REFRESH_TOKEN',
            'YOUTUBE_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return YouTubeClient(
            client_id=os.getenv('YOUTUBE_CLIENT_ID'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
            refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
            api_key=os.getenv('YOUTUBE_API_KEY')
        )
    
    def _init_telegram_client(self) -> TelegramClient:
        """Initialize Telegram client from environment variables.
        
        Returns:
            TelegramClient instance
        """
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        
        return TelegramClient(bot_token, chat_id, self.config)
    
    def run(self, test_mode: bool = False) -> Dict[str, Any]:
        """Run the monitoring process.
        
        Args:
            test_mode: If True, only test connections without processing
            
        Returns:
            Dictionary with execution results
        """
        logger.info("Starting YouTube subscription monitor...")
        
        try:
            # Test connections if requested
            if test_mode:
                return self._test_connections()
            
            # Get all subscriptions
            subscriptions = self.youtube_client.get_subscriptions()
            if not subscriptions:
                logger.warning("No subscriptions found")
                return self.stats
            
            logger.info(f"Found {len(subscriptions)} subscriptions")
            
            # Check each subscription for new videos
            for subscription in subscriptions:
                self._check_channel_for_new_videos(subscription)
            
            # Save state
            self.state_manager.save_state()
            
            # Log statistics
            logger.info(f"Monitoring complete. Stats: {self.stats}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            self.stats['errors'] += 1
            return self.stats
    
    def _check_channel_for_new_videos(self, subscription: Dict[str, Any]) -> None:
        """Check a channel for new videos and send notifications.
        
        Args:
            subscription: Subscription dictionary with channel info
        """
        channel_id = subscription['channel_id']
        channel_name = subscription['channel_title']
        
        logger.debug(f"Checking channel: {channel_name}")
        self.stats['channels_checked'] += 1
        
        try:
            # Get latest video from channel
            latest_video = self.youtube_client.get_latest_video(channel_id)
            
            if not latest_video:
                logger.debug(f"No videos found for channel: {channel_name}")
                return
            
            # Check if video is recent enough to notify about
            if not self._is_video_recent_enough(latest_video['published_at']):
                logger.debug(f"Video too old, skipping: {latest_video['title']} by {channel_name}")
                # Still update state to avoid checking this old video again
                self.state_manager.update_channel_state(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    latest_video_id=latest_video['video_id'],
                    video_timestamp=latest_video['published_at']
                )
                return
            
            # Check if this is a new video
            if self.state_manager.is_new_video(channel_id, latest_video['video_id']):
                logger.info(f"New video found: {latest_video['title']} by {channel_name}")
                self.stats['new_videos_found'] += 1
                
                # Send notification
                if self._send_notification(channel_name, latest_video):
                    # Update state only if notification was sent successfully
                    self.state_manager.update_channel_state(
                        channel_id=channel_id,
                        channel_name=channel_name,
                        latest_video_id=latest_video['video_id'],
                        video_timestamp=latest_video['published_at']
                    )
                    self.state_manager.increment_notification_count()
                    self.stats['notifications_sent'] += 1
            else:
                logger.debug(f"No new videos for channel: {channel_name}")
                
        except Exception as e:
            logger.error(f"Error checking channel {channel_name}: {e}")
            self.stats['errors'] += 1
    
    def _send_notification(self, channel_name: str, video: Dict[str, Any]) -> bool:
        """Send notification for a new video.
        
        Args:
            channel_name: Channel name
            video: Video dictionary
            
        Returns:
            True if notification sent successfully
        """
        if self.config['general'].get('dry_run', False):
            logger.info(f"[DRY RUN] Would send notification for: {video['title']}")
            return True
        
        return self.telegram_client.send_notification_sync(
            channel_name=channel_name,
            video_title=video['title'],
            video_id=video['video_id'],
            video_url=video['video_url'],
            published_at=video['published_at'],
            thumbnail_url=video.get('thumbnail_url')
        )
    
    def _is_video_recent_enough(self, published_at: str) -> bool:
        """Check if a video is recent enough to notify about.
        
        Args:
            published_at: Video publish timestamp (ISO format)
            
        Returns:
            True if video is recent enough (within configured days)
        """
        try:
            # Parse the published timestamp
            published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            
            # Get current time in UTC
            current_time = datetime.now(timezone.utc)
            
            # Get max age from config (default to 7 days)
            max_age_days = self.config.get("youtube", {}).get("max_video_age_days", 7)
            max_age = timedelta(days=max_age_days)
            
            # Check if video is within the time window
            age = current_time - published_time
            is_recent = age <= max_age
            
            logger.debug(f"Video age: {age.days} days, max allowed: {max_age_days} days, recent: {is_recent}")
            return is_recent
            
        except Exception as e:
            logger.error(f"Error checking video age: {e}")
            # If we can't parse the date, assume it's recent to be safe
            return True
    
    def _test_connections(self) -> Dict[str, Any]:
        """Test connections to YouTube and Telegram APIs.
        
        Returns:
            Test results dictionary
        """
        results = {
            'youtube': {'connected': False, 'error': None},
            'telegram': {'connected': False, 'error': None}
        }
        
        # Test YouTube connection
        logger.info("Testing YouTube API connection...")
        yt_success, yt_error = self.youtube_client.test_connection()
        results['youtube']['connected'] = yt_success
        results['youtube']['error'] = yt_error
        
        # Test Telegram connection
        logger.info("Testing Telegram bot connection...")
        tg_success = self.telegram_client.test_connection_sync()
        results['telegram']['connected'] = tg_success
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='YouTube Subscription Monitor')
    parser.add_argument('--test', action='store_true', help='Test connections only')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create and run monitor
        monitor = YouTubeMonitor(args.config)
        results = monitor.run(test_mode=args.test)
        
        # Exit with appropriate code
        if args.test:
            all_connected = all(results[service]['connected'] for service in results)
            sys.exit(0 if all_connected else 1)
        else:
            sys.exit(0 if results.get('errors', 0) == 0 else 1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
