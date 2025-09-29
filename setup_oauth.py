#!/usr/bin/env python3
"""OAuth2 setup helper for YouTube API authentication."""

import os
import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth2 scopes required for the application
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


def setup_oauth():
    """Guide user through OAuth2 setup process."""
    print("YouTube Subscription Monitor - OAuth2 Setup")
    print("=" * 50)
    print()
    
    # Check for credentials file
    creds_file = input("Enter path to OAuth2 credentials JSON file (from Google Cloud Console): ").strip()
    
    if not os.path.exists(creds_file):
        print(f"Error: Credentials file not found: {creds_file}")
        sys.exit(1)
    
    try:
        # Load credentials
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        # Extract client ID and secret
        if 'installed' in creds_data:
            client_id = creds_data['installed']['client_id']
            client_secret = creds_data['installed']['client_secret']
        elif 'web' in creds_data:
            client_id = creds_data['web']['client_id']
            client_secret = creds_data['web']['client_secret']
        else:
            print("Error: Invalid credentials file format")
            sys.exit(1)
        
        print(f"\nClient ID: {client_id[:20]}...")
        print("Client Secret: [HIDDEN]")
        print()
        
        # Run OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        
        print("Opening browser for authorization...")
        print("Please log in with the Google account whose YouTube subscriptions you want to monitor.")
        print()
        
        # Get credentials
        credentials = flow.run_local_server(port=0)
        
        print("\nAuthorization successful!")
        print()
        
        # Display the refresh token
        print("IMPORTANT: Save these values as GitHub Secrets:")
        print("=" * 50)
        print(f"YOUTUBE_CLIENT_ID={client_id}")
        print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
        print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
        print("=" * 50)
        print()
        
        # Save to env file if requested
        save_env = input("Save to .env file? (y/n): ").lower().strip() == 'y'
        
        if save_env:
            env_content = f"""# YouTube API Credentials
YOUTUBE_CLIENT_ID={client_id}
YOUTUBE_CLIENT_SECRET={client_secret}
YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}
YOUTUBE_API_KEY=YOUR_API_KEY_HERE

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("\nCredentials saved to .env file")
            print("NOTE: Don't forget to add your YouTube API key and Telegram credentials!")
            print("WARNING: Never commit the .env file to git!")
        
        print("\nSetup complete! Next steps:")
        print("1. Add all the secrets to your GitHub repository")
        print("2. Get your YouTube API key from Google Cloud Console")
        print("3. Create a Telegram bot and get your chat ID")
        print("4. Run 'python src/youtube_monitor.py --test' to test the setup")
        
    except Exception as e:
        print(f"\nError during OAuth setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_oauth()
