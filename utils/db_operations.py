#db_operations.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, Text
from contextlib import asynccontextmanager
import pandas as pd
import logging
from utils.parse_transform import parse_csv, deduplicate_data
import asyncio

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
            logging.error(f"Error during session: {e}")
            raise


#Function to insert CSV data into database
async def insert_to_db(df: pd.DataFrame):
    try:
        date_columns = ['BANKING_DATE', 'ACCOUNT_DATE_CLOSE']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        transactions = [Transaction(**record) for record in records if record['DOC_IDT']]

        async with get_session() as session:
            async with session.begin():  # Explicit transaction management
                session.add_all(transactions)
            await session.commit()
        logging.info(f"{len(transactions)} records inserted successfully.")
    except Exception as e:
        logging.error(f"Error inserting data: {e}")


#Function to Fetch data from the database
async def fetch_transactions(
        skip: int,
        limit: int,
        filter_by: str = None,
        filter_value: str = None,
        sort_by: str = None,
        sort_order: str = "asc"
) -> list[Transaction]:
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

    return transactions


#Processing CSV Data and Loading it before inserting it into DB
async def process_and_load_data(file_path):
    df = parse_csv(file_path)
    if not df.empty:
        deduplicated_df = await deduplicate_data(df, engine)
        await insert_to_db(deduplicated_df)
    else:
        logging.warning("Parsed DataFrame is empty. Skipping insertion.")
