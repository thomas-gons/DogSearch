import logging
import yaml
import os

# Configure environment to prevent conflicts with certain libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode="a"),  # log file
        logging.StreamHandler()  # also stream to terminal
    ]
)

logger = logging.getLogger(__name__)


with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
