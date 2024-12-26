"""
Configuration settings for the DOOM Discord bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Rate Limits
MESSAGE_RATE_LIMIT = 1.0  # 1 message per second to avoid rate limits
REACTION_RATE_LIMIT = 0.25  # 250ms between reaction updates

# ASCII Rendering settings
DISPLAY_WIDTH = int(os.getenv('DISPLAY_WIDTH', '60'))
DISPLAY_HEIGHT = int(os.getenv('DISPLAY_HEIGHT', '40'))
SHADE_CHARS = ' .:-=+*#%@'

# Game settings
UPDATE_RATE = float(os.getenv('UPDATE_RATE', '1.0'))  # 1 FPS to respect Discord rate limits
MAX_SESSIONS = int(os.getenv('MAX_SESSIONS', '10'))
SAVE_DIRECTORY = 'assets/saves'

# Discord settings
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
REACTION_TIMEOUT = 60.0  # seconds before reactions are cleared

# Rate Limit Protection
MAX_UPDATES_PER_MINUTE = 60  # Maximum updates per minute per channel
RATE_LIMIT_BUFFER = 0.1  # 100ms buffer between messages
BULK_DELETE_DELAY = 0.5  # 500ms delay between bulk message deletions

# Error messages
RATE_LIMIT_MESSAGE = " Slow down! Message rate limit reached. Wait a moment..."
SESSION_LIMIT_MESSAGE = " Maximum number of game sessions reached. Try again later."
