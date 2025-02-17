import json
import os
from utils.logger import setup_logger

logger = setup_logger()

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Override token with environment variable if available
        config['token'] = os.environ.get('DISCORD_BOT_TOKEN', config['token'])
        return config
    except FileNotFoundError:
        logger.error("Config file not found!")
        return None
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config file!")
        return None

def save_config(config):
    try:
        # Don't save the token to config file
        save_config = config.copy()
        save_config['token'] = 'YOUR_BOT_TOKEN_HERE'  # Replace with placeholder

        with open('config.json', 'w') as f:
            json.dump(save_config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False