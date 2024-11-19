#main.py
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from api.authorization import create_access_token, authenticate_user
from api.endpoints import router as api_router
from utils.db_operations import process_and_load_data, get_session, Transaction
from utils.fetch_files import fetch_files

# Configure logger
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

#Configure task executor
executor = ThreadPoolExecutor()

#Set up Lifespan
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


#Function to run background recurring tasks before startup
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

#Initialised API
app = FastAPI(lifespan=lifespan)

#Included endpoints
app.include_router(api_router, prefix="/api")

#Function for Authentication
@app.post("/api/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtain an access token by providing valid username and password.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

#Root
@app.get("/", tags=["Root"])
async def root():
    async with get_session() as session:
        transactions = await session.execute(select(Transaction).limit(10))
        transactions = transactions.scalars().all()
    return {
        "message": "Welcome to the Transaction API!",
        "sample_transactions": [tx for tx in transactions]
    }


#Defining where uvicorn should load main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
