#api/schemas.py
from pydantic import BaseModel, condecimal, conint
from datetime import date
from typing import Optional
from dotenv import load_dotenv

# Specify the path to the .env file
dotenv_path = "myenv/.env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

# Transaction model
class TransactionBase(BaseModel):
    INSTITUTION_BRANCH_CODE: Optional[conint(ge=0)]  # Allowing nulls or missing values
    BANKING_DATE: Optional[date]
    CONTRACT_NUMBER: Optional[str] = None
    PAN: Optional[str] = None
    DOC_IDT: Optional[str] = None
    SERVICE_CLASS: Optional[str] = None
    AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    TXN_CODE: Optional[str] = None
    TXN_NAME: Optional[str] = None
    TRANS_AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    TRANS_CURRENCY: Optional[conint(ge=0)] = None
    TRANS_DATE: Optional[date] = None
    EFFECTIVE_DATE: Optional[date] = None
    SETTLEMENT_DATE: Optional[date] = None
    PREVIOUS_DOC_IDT: Optional[str] = None
    CORRECTED_DOC_IDT: Optional[str] = None
    CORRECTION_TYPE: Optional[str] = None
    TRANS_PAYMENT_SCHEME: Optional[str] = None
    AUTH_CODE: Optional[str] = None
    TRANS_COUNTRY_CODE: Optional[str] = None
    TRANS_CITY: Optional[str] = None
    SETTL_CURRENCY: Optional[conint(ge=0)] = None
    SETTL_AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    DIRECTION: Optional[str] = None
    LOCAL_AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    TRANS_REASON: Optional[str] = None
    TRANS_DETAILS: Optional[str] = None
    TRANS_RRN: Optional[str] = None
    TRANS_ARN: Optional[str] = None
    TRANS_RESPONSE_CODE: Optional[str] = None
    TRANS_SRN: Optional[str] = None
    TRANS_MCC: Optional[conint(ge=0)] = None
    SOURCE_CHANNEL: Optional[str] = None
    TARGET_CHANNEL: Optional[str] = None
    MERCHANT: Optional[str] = None
    POSTING_STATUS: Optional[str] = None
    TRANS_INFO: Optional[str] = None
    SOURCE_ON_US_FLAG: Optional[str] = None
    TARGET_ON_US_FLAG: Optional[str] = None
    SOURCE_NUMBER: Optional[str] = None
    TARGET_NUMBER: Optional[str] = None
    OPER_TYPE_ADD_INFO: Optional[str] = None
    CONDITION_LIST: Optional[str] = None
    TRANSACTION_TYPE_NAME: Optional[str] = None
    TRANSACTION_TYPE_CODE: Optional[str] = None
    REQUEST_CATEGORY_NAME: Optional[str] = None
    SERVICE_CLASS_NAME: Optional[str] = None
    PAYMENT_SCHEME: Optional[str] = None
    PAYMENT_SCHEME_CODE: Optional[str] = None
    CARD_BRAND_NAME: Optional[str] = None
    CARD_BRAND_CODE: Optional[str] = None
    ACCOUNT_TYPE_NAME: Optional[str] = None
    ACCOUNT_CURRENCY: Optional[conint(ge=0)] = None
    ACCOUNT_NUMBER: Optional[str] = None
    ACCOUNT_NAME: Optional[str] = None
    GL_NUMBER: Optional[str] = None
    ACCOUNT_DATE_OPEN: Optional[date] = None
    ACCOUNT_DATE_CLOSE: Optional[date] = None
    SETTLEMENT_FX_RATE: Optional[condecimal(max_digits=18, decimal_places=6)] = None
    TRANSACTION_FX_RATE: Optional[condecimal(max_digits=18, decimal_places=6)] = None
    RBS_NUMBER: Optional[str] = None
    TRANS_CASH_AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    TRANS_CASH_CURR: Optional[conint(ge=0)] = None
    SETTL_CASH_AMOUNT: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    SETTL_CASH_CURR: Optional[conint(ge=0)] = None
    BASE_CURRENCY: Optional[conint(ge=0)] = None
    PARENT_CONTRACT_NUMBER: Optional[str] = None

    # PREVIOUS_DOC_IDT: Optional[str] = ''
    # CORRECTED_DOC_IDT: Optional[str] = ''
    # CORRECTION_TYPE: Optional[str] = ''
    # AUTH_CODE: Optional[str] = ''
    # DIRECTION: Optional[str] = ''
    # TRANS_REASON: Optional[str] = ''
    # TRANS_RRN: Optional[str] = ''
    # TRANS_RESPONSE_CODE: Optional[str] = ''
    # TRANS_SRN: Optional[str] = ''
    # RBS_NUMBER: Optional[str] = ''

    class Config:
        from_attributes = True
