import asyncio
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from dotenv import load_dotenv

from api.authorization import create_access_token, authenticate_user
from api.endpoints import router as api_router
from utils.db_operations import process_and_load_data, get_session, Transaction
from utils.fetch_files import fetch_files

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

# Configure task executor
executor = ThreadPoolExecutor()

# Set up Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global task
    try:
        logger.info("Initializing background task.")
        task = asyncio.create_task(periodic_task())
        yield
    except Exception as e:
        logger.error(f"Lifespan error: {e}")
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Periodic task cancelled.")

# Function to run background recurring tasks before startup
async def periodic_task():
    while True:
        try:
            logger.info("Fetching and processing new files.")
            await fetch_files()

            file_path = r"data\MOMORW_TRANSACTION_DUMP_20241031.csv"
            logger.info(f"Processing file: {file_path}")
            await process_and_load_data(file_path)

            logger.info("Periodic task completed successfully.")
        except Exception as e:
            logger.error(f"Error during periodic task: {e}")
        await asyncio.sleep(3600)

# Initialize API
app = FastAPI(lifespan=lifespan)

# Included endpoints
app.include_router(api_router, prefix="/api")

# Root
@app.get("/", tags=["Root"])
async def root():
    async with get_session() as session:
        transactions = await session.execute(select(Transaction).limit(10))
        transactions = transactions.scalars().all()
    return {
        "message": "Welcome to the Transaction API!",
        "sample_transactions": [tx for tx in transactions]
    }

# Define where uvicorn should load main
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),  # Using HOST from .env
        port=int(os.getenv("PORT", 8000)),  # Using PORT from .env
        log_level=os.getenv("LOG_LEVEL", "info"),  # Using LOG_LEVEL from .env
    )
