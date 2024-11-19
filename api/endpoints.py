#endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Security, Query
from sqlalchemy.orm import Session
from utils.db_operations import get_session, Transaction, fetch_transactions
from api.schemas import TransactionBase
from api.authorization import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

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

@router.get("/transactions", response_model=list[TransactionBase], tags=["Transactions"])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filter_by: str = Query(None, description="Column to filter by", enum=FILTER_COLUMNS),
    filter_value: str = Query(None, description="Value to filter with"),
    sort_by: str = Query(None, description="Column to sort by", enum=SORT_COLUMNS),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    """
    Retrieve paginated, filtered, and sorted transactions. Requires valid token.
    """
    token = credentials.credentials
    try:
        verify_token(token)
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        transactions = await fetch_transactions(
            skip=skip,
            limit=limit,
            filter_by=filter_by,
            filter_value=filter_value,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [TransactionBase.from_orm(tx) for tx in transactions]
    except Exception as e:
        logging.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Database error")
