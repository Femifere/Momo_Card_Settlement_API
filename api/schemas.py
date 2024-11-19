#schemas.py
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

# Transaction model
class TransactionBase(BaseModel):
    INSTITUTION_BRANCH_CODE: int
    BANKING_DATE: date
    CONTRACT_NUMBER: str
    PAN: str
    DOC_IDT: str
    SERVICE_CLASS: str
    AMOUNT: Decimal
    TXN_CODE: str
    TXN_NAME: str
    TRANS_AMOUNT: Decimal
    TRANS_CURRENCY: int
    TRANS_DATE: date
    EFFECTIVE_DATE: date
    SETTLEMENT_DATE: date
    PREVIOUS_DOC_IDT: str
    CORRECTED_DOC_IDT: str
    CORRECTION_TYPE: str
    TRANS_PAYMENT_SCHEME: str
    AUTH_CODE: str
    TRANS_COUNTRY_CODE: str
    TRANS_CITY: str
    SETTL_CURRENCY: int
    SETTL_AMOUNT: Decimal
    DIRECTION: str
    LOCAL_AMOUNT: Decimal
    TRANS_REASON: str
    TRANS_DETAILS: str
    TRANS_RRN: str
    TRANS_ARN: str
    TRANS_RESPONSE_CODE: str
    TRANS_SRN: str
    TRANS_MCC: int
    SOURCE_CHANNEL: str
    TARGET_CHANNEL: str
    MERCHANT: str
    POSTING_STATUS: str
    TRANS_INFO: str
    SOURCE_ON_US_FLAG: str
    TARGET_ON_US_FLAG: str
    SOURCE_NUMBER: str
    TARGET_NUMBER: str
    OPER_TYPE_ADD_INFO: str
    CONDITION_LIST: str
    TRANSACTION_TYPE_NAME: str
    TRANSACTION_TYPE_CODE: str
    REQUEST_CATEGORY_NAME: str
    SERVICE_CLASS_NAME: str
    PAYMENT_SCHEME: str
    PAYMENT_SCHEME_CODE: str
    CARD_BRAND_NAME: str
    CARD_BRAND_CODE: str
    ACCOUNT_TYPE_NAME: str
    ACCOUNT_CURRENCY: int
    ACCOUNT_NUMBER: str
    ACCOUNT_NAME: str
    GL_NUMBER: str
    ACCOUNT_DATE_OPEN: date
    ACCOUNT_DATE_CLOSE: date
    SETTLEMENT_FX_RATE: Decimal
    TRANSACTION_FX_RATE: Decimal
    RBS_NUMBER: str
    TRANS_CASH_AMOUNT: Decimal
    TRANS_CASH_CURR: int
    SETTL_CASH_AMOUNT: Decimal
    SETTL_CASH_CURR: int
    BASE_CURRENCY: int
    PARENT_CONTRACT_NUMBER: str

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models
