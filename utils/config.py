import os
from dotenv import load_dotenv
from utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger()

def load_config():

    config = {
        "TOKEN": os.getenv("DISCORD_BOT_TOKEN"),
        "prefix": os.getenv("prefix", "!"),
        "log_channel": os.getenv("log_channel"),
    }
    
    # Log missing values
    for key, value in config.items():
        if value is None:
            logger.warning(f"Missing environment variable: {key}")
    
    return config
# Load config values
CONFIG = load_config()
