import logging
import yaml
import os

# Configure environment to prevent conflicts with certain libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode="a"),  # Log to a file
        logging.StreamHandler()  # Also stream to terminal
    ]
)

# Initialize a logger for the application
logger = logging.getLogger(__name__)

# Load configuration from config.yaml
try:
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
except yaml.YAMLError as exc:
    logger.error("Error loading configuration: %s", exc)
