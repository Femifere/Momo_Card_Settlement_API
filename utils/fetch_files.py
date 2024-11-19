#fetch_files.py
import os
import logging
import shutil
import pandas as pd

LOCAL_PATH = r"C:\Users\fresh\Documents\Momo Card Settlement Project\MOMORW_TRANSACTION_DUMP_20241031.csv"
LOCAL_SAVE_PATH = r"C:\Users\fresh\Documents\Momo Card Settlement Project\data"

async def fetch_files():
    try:
        os.makedirs(LOCAL_SAVE_PATH, exist_ok=True)
        shutil.copy(LOCAL_PATH, LOCAL_SAVE_PATH)
        logging.info(f"File successfully copied from {LOCAL_PATH} to {LOCAL_SAVE_PATH}")
    except FileNotFoundError:
        logging.error(f"File not found at {LOCAL_PATH}")
    except Exception as e:
        logging.error(f"Failed to fetch and process file: {e}")

