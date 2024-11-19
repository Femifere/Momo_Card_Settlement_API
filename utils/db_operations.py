#db_operations.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, Text
from contextlib import asynccontextmanager
import pandas as pd
import logging
from utils.parse_transform import parse_csv, deduplicate_data
import asyncio
import logging
import sys

# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
)

# Get a logger instance
logger = logging.getLogger(__name__)


#using aiomysql driver to connect to mySQL Database
DATABASE_URL = "mysql+aiomysql://root@127.0.0.1:3306/momo_card_settlement"

# Configured async SQLAlchemy engine and session
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


#Session
@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error during session: {e}")
            raise


# Function to insert CSV data into the database
async def insert_to_db(df: pd.DataFrame):
    try:
        logger.info("Starting the insertion process.")

        # Convert date columns to datetime
        date_columns = ['BANKING_DATE', 'ACCOUNT_DATE_CLOSE']
        for col in date_columns:
            if col in df.columns:
                logger.info(f"Converting column '{col}' to datetime.")
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.info(f"Column '{col}' converted to datetime.")
        logger.info("Date columns converted to datetime.")

        # Replace NaN with None for compatibility with SQLAlchemy
        logger.info("Replacing NaN values with None.")
        df = df.where(pd.notnull(df), None)
        logger.info("NaN values replaced with None.")

        # Ensure the DataFrame has the primary key column
        if 'DOC_IDT' not in df.columns:
            logger.warning("DOC_IDT column not found in the DataFrame. Skipping insertion.")
            return

        # Filter out rows without primary key values
        logger.info(f"Filtering rows without DOC_IDT values. Initial row count: {len(df)}.")
        df = df[df['DOC_IDT'].notnull()]
        logger.info(f"Row count after filtering: {len(df)}.")

        if df.empty:
            logger.info("No valid records to insert after filtering. Skipping insertion.")
            return

        logger.info(f"Preparing to deduplicate {len(df)} records based on DOC_IDT.")

        # Deduplicate by checking existing records in the database
        doc_ids_to_check = df['DOC_IDT'].unique().tolist()
        logger.info(f"Unique DOC_IDTs to check in the database: {doc_ids_to_check[:10]}... (showing first 10)")

        async with get_session() as session:
            # Fetch existing DOC_IDTs in the database
            existing_query = select(Transaction.DOC_IDT).where(Transaction.DOC_IDT.in_(doc_ids_to_check))
            logger.info(f"Executing query to fetch existing DOC_IDTs: {existing_query}")
            result = await session.execute(existing_query)
            existing_doc_ids = {row[0] for row in result}

        logger.info(f"Found {len(existing_doc_ids)} existing records in the database.")

        # Filter out existing records
        logger.info(f"Filtering out existing DOC_IDTs. DataFrame size before: {len(df)}.")
        unique_records_df = df[~df['DOC_IDT'].isin(existing_doc_ids)]
        logger.info(f"DataFrame size after filtering: {len(unique_records_df)}.")

        # If no unique records, exit early
        if unique_records_df.empty:
            logger.info("No new records to insert after deduplication. Exiting.")
            return

        # Convert unique records to a list of dictionaries for bulk insert
        new_records_dict = unique_records_df.to_dict(orient='records')
        logger.info(f"Prepared {len(new_records_dict)} records for insertion.")

        # Create the bulk insert query with on_duplicate_key_update to handle duplicates
        stmt = insert(Transaction).values(new_records_dict)
        stmt = stmt.on_duplicate_key_update(
            {col.name: col for col in stmt.inserted}
        )
        logger.info(f"Generated bulk insert statement: {stmt}")

        # Perform the bulk insert
        async with get_session() as session:
            logger.info(f"Executing bulk insert of {len(new_records_dict)} records.")
            await session.execute(stmt)
            await session.commit()

        logger.info(f"{len(new_records_dict)} unique records inserted successfully.")

    except Exception as e:
        logger.error(f"Error during insertion: {e}")


# Function to fetch data from the database
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


#Processing CSV Data and Loading it before inserting it into DB
async def process_and_load_data(file_path):
    df = parse_csv(file_path)
    if not df.empty:
        deduplicated_df = await deduplicate_data(df, engine)
        await insert_to_db(deduplicated_df)
    else:
        logger.warning("Parsed DataFrame is empty. Skipping insertion.")
