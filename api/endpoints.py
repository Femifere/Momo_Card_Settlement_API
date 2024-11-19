#endpoints.py
import json
import os

from fastapi import APIRouter, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator

from api.authorization import verify_token
from api.schemas import TransactionBase
from utils.db_operations import fetch_transactions
from api.shared import load_users, save_users

router = APIRouter()
bearer_scheme = HTTPBearer()

# Available columns for filtering and sorting
FILTER_COLUMNS = [
    "INSTITUTION_BRANCH_CODE", "BANKING_DATE", "DOC_IDT", "SERVICE_CLASS", "AMOUNT", "TXN_CODE", "TXN_NAME",
    "TRANS_AMOUNT", "TRANS_CURRENCY", "TRANS_DATE", "EFFECTIVE_DATE", "SETTLEMENT_DATE", "PREVIOUS_DOC_IDT",
    "CORRECTED_DOC_IDT", "CORRECTION_TYPE", "TRANS_PAYMENT_SCHEME", "AUTH_CODE", "TRANS_COUNTRY_CODE",
    "TRANS_CITY", "SETTL_CURRENCY", "SETTL_AMOUNT", "DIRECTION", "LOCAL_AMOUNT", "TRANS_REASON", "TRANS_DETAILS",
    "TRANS_RRN", "TRANS_ARN", "TRANS_RESPONSE_CODE", "TRANS_SRN", "TRANS_MCC", "SOURCE_CHANNEL", "TARGET_CHANNEL",
    "MERCHANT", "POSTING_STATUS", "TRANS_INFO", "SOURCE_ON_US_FLAG", "TARGET_ON_US_FLAG", "SOURCE_NUMBER",
    "TARGET_NUMBER", "OPER_TYPE_ADD_INFO", "CONDITION_LIST", "TRANSACTION_TYPE_NAME", "TRANSACTION_TYPE_CODE",
    "REQUEST_CATEGORY_NAME", "SERVICE_CLASS_NAME", "PAYMENT_SCHEME", "PAYMENT_SCHEME_CODE", "CARD_BRAND_NAME",
    "CARD_BRAND_CODE", "ACCOUNT_TYPE_NAME", "ACCOUNT_CURRENCY", "ACCOUNT_NUMBER", "ACCOUNT_NAME", "GL_NUMBER",
    "ACCOUNT_DATE_OPEN", "ACCOUNT_DATE_CLOSE", "SETTLEMENT_FX_RATE", "TRANSACTION_FX_RATE", "RBS_NUMBER",
    "TRANS_CASH_AMOUNT", "TRANS_CASH_CURR", "SETTL_CASH_AMOUNT", "SETTL_CASH_CURR", "BASE_CURRENCY", "PARENT_CONTRACT_NUMBER"
]

SORT_COLUMNS = FILTER_COLUMNS.copy()  # Same as filter columns for sorting

# File location for secure storage
USERS_FILE = r"data\users.json"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize users file if it doesn't exist
def initialize_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as file:
            json.dump({}, file)

initialize_users_file()

# Load all users
def load_users():
    with open(USERS_FILE, "r") as file:
        return json.load(file)

# Save users
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

# User registration model
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter.")
        return value

# Get Transactions Endpoint
@router.get("/transactions", response_model=list[TransactionBase], tags=["Transactions"])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filter_by: str = Query(None, enum=FILTER_COLUMNS),
    filter_value: str = Query(None),
    sort_by: str = Query(None, enum=SORT_COLUMNS),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    token = credentials.credentials
    try:
        verify_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        transactions = await fetch_transactions(
            skip=skip, limit=limit, filter_by=filter_by, filter_value=filter_value, sort_by=sort_by, sort_order=sort_order
        )
        return [TransactionBase.from_orm(tx) for tx in transactions]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

# Register User Endpoint
@router.post("/register", tags=["User Management"])
async def register_user(user: UserRegistration):
    users = load_users()
    if user.email in users:
        raise HTTPException(status_code=400, detail="User already exists.")
    users[user.email] = {"password": pwd_context.hash(user.password)}
    save_users(users)
    return {"message": "User registered successfully!"}
