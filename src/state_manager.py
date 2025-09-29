"""State management for tracking notified videos."""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Manages the state file for tracking notified videos."""
    
    def __init__(self, state_file_path: str = "data/state.json"):
        """Initialize the state manager.
        
        Args:
            state_file_path: Path to the state JSON file
        """
        self.state_file_path = state_file_path
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file or create default state.
        
        Returns:
            Dictionary containing the state
        """
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading state file: {e}")
                return self._default_state()
        else:
            logger.info("State file not found, creating default state")
            return self._default_state()
    
    def _default_state(self) -> Dict[str, Any]:
        """Create default state structure.
        
        Returns:
            Default state dictionary
        """
        return {
            "channels": {},
            "metadata": {
                "last_run": None,
                "total_notifications_sent": 0,
                "version": "1.0.0"
            }
        }
    
    def save_state(self) -> None:
        """Save current state to file."""
        # Update last run timestamp
        self.state["metadata"]["last_run"] = datetime.utcnow().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        
        # Write state to file
        with open(self.state_file_path, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        logger.info("State saved successfully")
    
    def get_channel_state(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get state for a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel state dictionary or None if not found
        """
        return self.state["channels"].get(channel_id)
    
    def update_channel_state(self, channel_id: str, channel_name: str, 
                           latest_video_id: str, video_timestamp: str) -> None:
        """Update state for a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            channel_name: Channel display name
            latest_video_id: ID of the latest video
            video_timestamp: Timestamp of the latest video
        """
        self.state["channels"][channel_id] = {
            "name": channel_name,
            "latest_video_id": latest_video_id,
            "latest_video_timestamp": video_timestamp,
            "last_checked": datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Updated state for channel {channel_name} ({channel_id})")
    
    def is_new_video(self, channel_id: str, video_id: str) -> bool:
        """Check if a video is new (not previously notified).
        
        Args:
            channel_id: YouTube channel ID
            video_id: YouTube video ID
            
        Returns:
            True if video is new, False otherwise
        """
        channel_state = self.get_channel_state(channel_id)
        
        if channel_state is None:
            # First time seeing this channel
            return True
        
        # Check if this video is different from the last notified one
        return channel_state.get("latest_video_id") != video_id
    
    def increment_notification_count(self) -> None:
        """Increment the total notification count."""
        self.state["metadata"]["total_notifications_sent"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from the state.
        
        Returns:
            Dictionary containing statistics
        """
        return {
            "total_channels_tracked": len(self.state["channels"]),
            "total_notifications_sent": self.state["metadata"]["total_notifications_sent"],
            "last_run": self.state["metadata"]["last_run"]
        }
