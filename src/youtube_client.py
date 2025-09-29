"""YouTube API client for fetching subscriptions and videos."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeClient:
    """Client for interacting with YouTube Data API."""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, api_key: str):
        """Initialize YouTube client.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            refresh_token: OAuth2 refresh token
            api_key: YouTube API key
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.api_key = api_key
        self.youtube = self._build_youtube_client()
    
    def _build_youtube_client(self):
        """Build authenticated YouTube API client.
        
        Returns:
            Authenticated YouTube API client
        """
        # Create credentials from refresh token
        credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        
        # Refresh the access token
        credentials.refresh(Request())
        
        # Build YouTube API client
        return build('youtube', 'v3', credentials=credentials)
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all channel subscriptions for the authenticated user.
        
        Returns:
            List of subscription dictionaries
        """
        subscriptions = []
        next_page_token = None
        
        try:
            while True:
                # Request subscriptions
                request = self.youtube.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                # Extract subscription data
                for item in response.get('items', []):
                    subscription = {
                        'channel_id': item['snippet']['resourceId']['channelId'],
                        'channel_title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                    }
                    subscriptions.append(subscription)
                
                # Check for next page
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            logger.info(f"Fetched {len(subscriptions)} subscriptions")
            return subscriptions
            
        except HttpError as e:
            logger.error(f"Error fetching subscriptions: {e}")
            return []
    
    def get_channel_videos(self, channel_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get recent videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return
            
        Returns:
            List of video dictionaries
        """
        try:
            # Get channel uploads playlist ID
            channel_request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get recent videos from uploads playlist
            videos_request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            videos_response = videos_request.execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video = {
                    'video_id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url'),
                    'video_url': f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}"
                }
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            logger.error(f"Error fetching videos for channel {channel_id}: {e}")
            return []
    
    def get_latest_video(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest video from a channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Latest video dictionary or None if no videos found
        """
        videos = self.get_channel_videos(channel_id, max_results=1)
        return videos[0] if videos else None
    
    def search_channel_videos(self, channel_id: str, published_after: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Search for videos from a channel published after a certain date.
        
        Args:
            channel_id: YouTube channel ID
            published_after: Optional datetime to filter videos
            
        Returns:
            List of video dictionaries
        """
        try:
            # Default to videos from last 24 hours if no date specified
            if published_after is None:
                published_after = datetime.utcnow() - timedelta(days=1)
            
            # Format date for API
            published_after_str = published_after.isoformat() + 'Z'
            
            # Search for videos
            search_request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                order="date",
                publishedAfter=published_after_str,
                maxResults=10
            )
            search_response = search_request.execute()
            
            videos = []
            for item in search_response.get('items', []):
                video = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url'),
                    'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            logger.error(f"Error searching videos for channel {channel_id}: {e}")
            return []
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test YouTube API connection and authentication.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Try to get authenticated user's channel
            request = self.youtube.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel_name = response['items'][0]['snippet']['title']
                logger.info(f"YouTube API connected successfully. Authenticated as: {channel_name}")
                return True, None
            else:
                return True, "Connected but no channel found for user"
                
        except Exception as e:
            error_msg = f"YouTube API connection failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
