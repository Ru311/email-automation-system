import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("gmail-ai")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/app.log", mode="w")
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)