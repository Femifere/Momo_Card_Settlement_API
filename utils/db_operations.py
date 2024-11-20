#db_operations.py
from dotenv import load_dotenv
load_dotenv()

import logging
import os
from contextlib import asynccontextmanager

import pandas as pd
from pydantic import ValidationError

from api.schemas import TransactionBase
from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, Text
from sqlalchemy import insert
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from utils.parse_transform import parse_csv, deduplicate_data

# Configure the logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database configuration
# Load database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root@127.0.0.1:3306/momo_card_settlement")

engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Transaction model
class Transaction(Base):
    __tablename__ = 'transactions'

    INSTITUTION_BRANCH_CODE = Column(Integer)
    BANKING_DATE = Column(Date)
    CONTRACT_NUMBER = Column(String(255))
    PAN = Column(String(255))
    DOC_IDT = Column(String(255), primary_key=True)
    SERVICE_CLASS = Column(CHAR(1))
    AMOUNT = Column(DECIMAL(18, 2))
    TXN_CODE = Column(String(255))
    TXN_NAME = Column(String(255))
    TRANS_AMOUNT = Column(DECIMAL(18, 2))
    TRANS_CURRENCY = Column(Integer)
    TRANS_DATE = Column(Date)
    EFFECTIVE_DATE = Column(Date)
    SETTLEMENT_DATE = Column(Date)
    PREVIOUS_DOC_IDT = Column(String(255))
    CORRECTED_DOC_IDT = Column(String(255))
    CORRECTION_TYPE = Column(String(255))
    TRANS_PAYMENT_SCHEME = Column(String(255))
    AUTH_CODE = Column(String(255))
    TRANS_COUNTRY_CODE = Column(String(255))
    TRANS_CITY = Column(String(255))
    SETTL_CURRENCY = Column(Integer)
    SETTL_AMOUNT = Column(DECIMAL(18, 2))
    DIRECTION = Column(String(255))
    LOCAL_AMOUNT = Column(DECIMAL(18, 2))
    TRANS_REASON = Column(String(255))
    TRANS_DETAILS = Column(Text)
    TRANS_RRN = Column(String(255))
    TRANS_ARN = Column(String(255))
    TRANS_RESPONSE_CODE = Column(String(255))
    TRANS_SRN = Column(String(255))
    TRANS_MCC = Column(Integer)
    SOURCE_CHANNEL = Column(String(255))
    TARGET_CHANNEL = Column(String(255))
    MERCHANT = Column(String(255))
    POSTING_STATUS = Column(String(255))
    TRANS_INFO = Column(Text)
    SOURCE_ON_US_FLAG = Column(CHAR(1))
    TARGET_ON_US_FLAG = Column(CHAR(1))
    SOURCE_NUMBER = Column(String(255))
    TARGET_NUMBER = Column(String(255))
    OPER_TYPE_ADD_INFO = Column(Text)
    CONDITION_LIST = Column(Text)
    TRANSACTION_TYPE_NAME = Column(String(255))
    TRANSACTION_TYPE_CODE = Column(String(255))
    REQUEST_CATEGORY_NAME = Column(String(255))
    SERVICE_CLASS_NAME = Column(String(255))
    PAYMENT_SCHEME = Column(String(255))
    PAYMENT_SCHEME_CODE = Column(String(255))
    CARD_BRAND_NAME = Column(String(255))
    CARD_BRAND_CODE = Column(String(255))
    ACCOUNT_TYPE_NAME = Column(String(255))
    ACCOUNT_CURRENCY = Column(Integer)
    ACCOUNT_NUMBER = Column(String(255))
    ACCOUNT_NAME = Column(String(255))
    GL_NUMBER = Column(String(255))
    ACCOUNT_DATE_OPEN = Column(Date)
    ACCOUNT_DATE_CLOSE = Column(Date)
    SETTLEMENT_FX_RATE = Column(DECIMAL(18, 6))
    TRANSACTION_FX_RATE = Column(DECIMAL(18, 6))
    RBS_NUMBER = Column(String(255))
    TRANS_CASH_AMOUNT = Column(DECIMAL(18, 2))
    TRANS_CASH_CURR = Column(Integer)
    SETTL_CASH_AMOUNT = Column(DECIMAL(18, 2))
    SETTL_CASH_CURR = Column(Integer)
    BASE_CURRENCY = Column(Integer)
    PARENT_CONTRACT_NUMBER = Column(String(255))


# Synchronous table creation
def create_tables():
    import sqlalchemy
    sync_engine = sqlalchemy.create_engine(DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql"))
    Base.metadata.create_all(sync_engine)


create_tables()



# Session management
@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error during session: {e}")
            raise


# Improved preprocessing with logging
async def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the data: convert dates, handle NaNs, and filter invalid rows."""
    logger.info("Starting data preprocessing.")

    # Convert date columns to datetime
    date_columns = ['BANKING_DATE', 'ACCOUNT_DATE_CLOSE']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Replace NaN with None for SQLAlchemy compatibility
    df = df.where(pd.notnull(df), None)

    # Filter out rows without 'DOC_IDT'
    df = df[df['DOC_IDT'].notnull()]

    logger.info(f"Preprocessing complete. Valid rows count: {len(df)}.")
    return df


# Enhanced function to fetch existing DOC_IDT values with detailed logging
async def get_existing_doc_ids(doc_ids: list) -> set:
    """Fetch existing DOC_IDT values from the database with detailed logging."""
    logger.info(f"Fetching existing DOC_IDT values for {len(doc_ids)} records from the database.")
    async with get_session() as session:
        try:
            existing_query = select(Transaction.DOC_IDT).where(Transaction.DOC_IDT.in_(doc_ids))
            result = await session.execute(existing_query)
            existing_ids = {row[0] for row in result}
            logger.debug(f"Fetched existing DOC_IDT values: {existing_ids}")
            return existing_ids
        except Exception as e:
            logger.error(f"Error fetching existing DOC_IDT values: {e}")
            return set()


# Improved filtering with logging
def filter_new_records(df: pd.DataFrame, existing_ids: set) -> pd.DataFrame:
    """Filter out rows with existing DOC_IDT values, with detailed logging."""
    initial_count = len(df)
    logger.info(f"Starting filtering process. Initial DataFrame size: {initial_count}.")

    # Log the type of existing_ids to ensure it's a set of strings
    logger.info(f"Existing DOC_IDT values fetched from DB: {len(existing_ids)}")
    logger.debug(f"Type of existing_ids: {type(existing_ids)}")

    # Ensure existing_ids is a set of strings (in case it's not)
    existing_ids = {str(id) for id in existing_ids}
    logger.debug(f"Converted existing_ids to string type: {existing_ids}")

    filtered_rows = []
    for index, row in df.iterrows():
        doc_id = row['DOC_IDT']

        # Log the type of DOC_IDT to ensure it's a string
        logger.debug(f"Processing row {index} with DOC_IDT: {doc_id} (Type: {type(doc_id)})")

        # Ensure DOC_IDT is treated as a string for accurate comparison
        if isinstance(doc_id, str):
            doc_id = doc_id.strip()  # Remove any potential leading/trailing whitespace
            logger.debug(f"Stripped DOC_IDT: {doc_id}")
        else:
            logger.warning(f"DOC_IDT in row {index} is not a string, converting to string.")
            doc_id = str(doc_id)

        if doc_id in existing_ids:
            logger.info(f"Skipping existing records...")
        else:
            logger.debug(f"New record identified: DOC_IDT={doc_id}, Row={row.to_dict()}")
            filtered_rows.append(row)

    df_filtered = pd.DataFrame(filtered_rows, columns=df.columns)
    logger.info(f"Filtered out {initial_count - len(df_filtered)} rows. Remaining rows: {len(df_filtered)}.")
    return df_filtered


# Insert records with logging
async def insert_unique_records(df: pd.DataFrame):
    """Insert unique records into the database."""
    try:
        records = []
        # Convert DataFrame rows to TransactionBase models
        for index, row in df.iterrows():
            transaction_data = row.to_dict()
            logger.debug(f"Row {index} data types: {[(k, type(v)) for k, v in transaction_data.items()]}")
            try:
                # Create a Pydantic model instance (Validation)
                try:
                    transaction = TransactionBase(**transaction_data)
                except ValidationError as e:
                    logger.error(f"Validation error for row {index}: {e.errors()}")
                    continue
                records.append(transaction.dict())  # Get dictionary representation for insertion
            except Exception as e:
                logger.error(f"Error creating Pydantic model for row {index}: {e}")
                continue

        if not records:
            logger.warning("No valid records to insert.")
            return

        logger.debug(f"Preparing to insert records: {records}")

        # Generate the SQL statement
        stmt = insert(Transaction).values(records)
        stmt = stmt.on_duplicate_key_update(
            {col.name: col for col in stmt.inserted}
        )

        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()

        logger.info(f"Inserted {len(records)} new records.")
    except Exception as e:
        logger.error(f"Error during unique records insertion: {e}")

# Main function with logging and error handling
async def process_and_insert_data(df: pd.DataFrame):
    """Main function to process and insert data into the database."""
    try:
        logger.info("Starting data insertion process.")

        # Preprocess the data
        df = await preprocess_data(df)
        if df.empty:
            logger.info("No valid records to process. Exiting.")
            return

        # Get unique DOC_IDT values to check in the database
        unique_ids = df['DOC_IDT'].unique().tolist()
        logger.info(f"Extracted {len(unique_ids)} unique DOC_IDT values for deduplication.")

        # Fetch existing DOC_IDT values from the database
        existing_ids = await get_existing_doc_ids(unique_ids)
        logger.info(f"Found {len(existing_ids)} existing DOC_IDT values in the database.")

        # Filter out existing records
        logger.info("Starting record filtering...")
        df_new = filter_new_records(df, existing_ids)
        if df_new.empty:
            logger.info("No new records to insert after filtering. Exiting.")
            return

        # Insert new records
        logger.info(f"Inserting {len(df_new)} new records into the database.")
        await insert_unique_records(df_new)
        logger.info("Data insertion process completed successfully.")
    except Exception as e:
        logger.error(f"Error during the insertion process: {e}")


# Function to fetch data from the database (remains unchanged)
async def fetch_transactions(
        skip: int,
        limit: int,
        filter_by: str = None,
        filter_value: str = None,
        sort_by: str = None,
        sort_order: str = "asc"
) -> list[Transaction]:
    try:
        query = select(Transaction).offset(skip).limit(limit)

        # Apply filtering if requested
        if filter_by and filter_value:
            filter_condition = getattr(Transaction, filter_by) == filter_value
            query = query.where(filter_condition)

        # Apply sorting if requested
        if sort_by:
            if sort_order == "asc":
                query = query.order_by(getattr(Transaction, sort_by).asc())
            else:
                query = query.order_by(getattr(Transaction, sort_by).desc())

        # Execution of the query
        async with get_session() as session:
            result = await session.execute(query)
            transactions = result.scalars().all()

        logger.info(f"Fetched {len(transactions)} transactions from the database.")
        return transactions

    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        return []


# Function to process and load data from CSV file
async def process_and_load_data(file_path):
    df = parse_csv(file_path)
    if not df.empty:
        deduplicated_df = await deduplicate_data(df, engine)
        await process_and_insert_data(deduplicated_df)
    else:
        logger.warning("Parsed DataFrame is empty. Skipping insertion.")
