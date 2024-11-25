#utils/fetch_files.py
from dotenv import load_dotenv
# Specify the path to the .env file
dotenv_path = "myenv/.env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

import os
import logging
import shutil
import pandas as pd

#Local Path and Repository path

LOCAL_PATH = os.getenv("LOCAL_PATH", "app/MOMORW_TRANSACTION_DUMP_20241031.csv")
LOCAL_SAVE_PATH = os.getenv("LOCAL_SAVE_PATH", "app/data/")

#Function to fetch files from the repository
async def fetch_files():
    try:
        os.makedirs(LOCAL_SAVE_PATH, exist_ok=True)
        shutil.copy(LOCAL_PATH, LOCAL_SAVE_PATH)
        logging.info(f"File successfully copied from {LOCAL_PATH} to {LOCAL_SAVE_PATH}")
    except FileNotFoundError:
        logging.error(f"File not found at {LOCAL_PATH}")
    except Exception as e:
        logging.error(f"Failed to fetch and process file: {e}")

