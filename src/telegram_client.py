"""Telegram bot client for sending notifications."""

import logging
from typing import Optional, Dict, Any
import telegram
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from datetime import datetime, timezone
import pytz

logger = logging.getLogger(__name__)


class TelegramClient:
    """Client for sending notifications via Telegram."""
    
    def __init__(self, bot_token: str, chat_id: str, config: Dict[str, Any]):
        """Initialize Telegram client.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
            config: Configuration dictionary
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.config = config
        self.bot = Bot(token=bot_token)
        
    async def send_notification(self, channel_name: str, video_title: str, 
                              video_id: str, video_url: str, 
                              published_at: str, thumbnail_url: Optional[str] = None) -> bool:
        """Send a notification about a new video.
        
        Args:
            channel_name: YouTube channel name
            video_title: Video title
            video_id: YouTube video ID
            video_url: Full URL to the video
            published_at: Video publish timestamp
            thumbnail_url: Optional thumbnail URL
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Calculate time ago
            time_ago = self._calculate_time_ago(published_at)
            
            # Format message using template
            message_text = self.config["telegram"]["notification_template"].format(
                channel_name=channel_name,
                video_title=video_title,
                video_url=video_url,
                time_ago=time_ago
            )
            
            # Send message
            if thumbnail_url and not self.config["general"].get("dry_run", False):
                # Send with thumbnail
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=thumbnail_url,
                    caption=message_text,
                    parse_mode=self.config["telegram"].get("parse_mode", ParseMode.HTML),
                    disable_web_page_preview=self.config["telegram"].get("disable_web_page_preview", False)
                )
            else:
                # Send text only
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message_text,
                    parse_mode=self.config["telegram"].get("parse_mode", ParseMode.HTML),
                    disable_web_page_preview=self.config["telegram"].get("disable_web_page_preview", False)
                )
            
            logger.info(f"Notification sent for video: {video_title} by {channel_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def send_notification_sync(self, channel_name: str, video_title: str,
                             video_id: str, video_url: str, 
                             published_at: str, thumbnail_url: Optional[str] = None) -> bool:
        """Synchronous wrapper for send_notification.
        
        Args:
            Same as send_notification
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Create new event loop if none exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.send_notification(
                channel_name, video_title, video_id, 
                video_url, published_at, thumbnail_url
            )
        )
    
    async def test_connection(self) -> bool:
        """Test the Telegram bot connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            me = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{me.username}")
            
            # Send test message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ YouTube Subscription Monitor connected successfully!"
            )
            return True
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def test_connection_sync(self) -> bool:
        """Synchronous wrapper for test_connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.test_connection())
    
    def _calculate_time_ago(self, published_at: str) -> str:
        """Calculate human-readable time ago string.
        
        Args:
            published_at: ISO format timestamp
            
        Returns:
            Human-readable time ago string
        """
        try:
            # Parse the published timestamp
            published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            
            # Get current time in UTC
            current_time = datetime.now(timezone.utc)
            
            # Calculate difference
            time_diff = current_time - published_time
            
            # Convert to human-readable format
            if time_diff.days > 0:
                if time_diff.days == 1:
                    return "1 day ago"
                else:
                    return f"{time_diff.days} days ago"
            
            hours = time_diff.seconds // 3600
            if hours > 0:
                if hours == 1:
                    return "1 hour ago"
                else:
                    return f"{hours} hours ago"
            
            minutes = (time_diff.seconds % 3600) // 60
            if minutes > 0:
                if minutes == 1:
                    return "1 minute ago"
                else:
                    return f"{minutes} minutes ago"
            
            return "Just now"
            
        except Exception as e:
            logger.error(f"Error calculating time ago: {e}")
            return "Recently"
