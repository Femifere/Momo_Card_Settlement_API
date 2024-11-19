#parse_transform.py
import pandas as pd
import logging
from sqlalchemy.sql import text

logging.basicConfig(level=logging.INFO)


def parse_csv(file_path, default_date='1900-01-01'):
    try:
        logging.info(f"Processing file: {file_path}")

        # Read the file with appropriate delimiter and options
        df = pd.read_csv(file_path, sep="|", engine='python', skip_blank_lines=True)

        # Clean column names to remove extra commas or spaces
        df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
        df.columns = df.columns.str.replace(r",+$", "", regex=True)  # Remove trailing commas

        # Fill missing values with column-specific defaults
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')  # Replace missing strings with empty string
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)  # Replace missing numeric values with 0
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].fillna(pd.NaT)  # Replace missing dates with NaT

        # Process and convert specific column groups
        date_columns = ['BANKING_DATE', 'TRANS_DATE', 'EFFECTIVE_DATE', 'SETTLEMENT_DATE', 'ACCOUNT_DATE_OPEN',
                        'ACCOUNT_DATE_CLOSE']
        numeric_columns = ['AMOUNT', 'TRANS_AMOUNT', 'SETTLEMENT_FX_RATE', 'TRANSACTION_FX_RATE', 'TRANS_CASH_AMOUNT',
                           'SETTL_CASH_AMOUNT', 'LOCAL_AMOUNT']

        for col in date_columns:
            if col in df.columns:
                # Specify a consistent format if possible, otherwise rely on 'coerce'
                df[col] = pd.to_datetime(df[col], format='%d-%b-%y', errors='coerce')

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, coerce invalid entries to NaN

        # Handle columns with special formats like JSON, lists, or nested data
        if 'CONDITION_LIST' in df.columns:
            df['CONDITION_LIST'] = df['CONDITION_LIST'].apply(
                lambda x: x.split(';') if isinstance(x, str) else []
            )

        # Drop rows with missing essential identifiers (e.g., 'DOC_IDT')
        if 'DOC_IDT' in df.columns:
            df = df.dropna(subset=['DOC_IDT'])

        # Log invalid data for dates (NaT values)
        invalid_dates = df[df['ACCOUNT_DATE_CLOSE'].isna()]
        if not invalid_dates.empty:
            logging.warning(f"Invalid 'ACCOUNT_DATE_CLOSE' dates found in rows: {invalid_dates.index.tolist()}")
            logging.warning(f"Sample of invalid rows: {invalid_dates[['ACCOUNT_DATE_CLOSE']].head()}")

            # Replace NaT with the default date
            df['ACCOUNT_DATE_CLOSE'] = df['ACCOUNT_DATE_CLOSE'].fillna(pd.to_datetime(default_date))

        logging.info("File processed successfully.")
        return df

    except Exception as e:
        logging.error(f"Error parsing CSV: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error



async def deduplicate_data(df, engine):
    try:
        # Use an asynchronous connection
        async with engine.connect() as conn:
            # Use the text() function to execute a raw SQL query
            result = await conn.execute(text("SELECT DOC_IDT FROM transactions"))

            # Fetch results and convert to a pandas DataFrame
            existing_ids = pd.DataFrame(result.fetchall(), columns=['DOC_IDT'])

        # Ensure the DOC_IDT column is present in the DataFrame
        if 'DOC_IDT' in df.columns:
            unique_df = df[~df['DOC_IDT'].isin(existing_ids['DOC_IDT'])]
        else:
            logging.warning("DOC_IDT column missing from DataFrame. Skipping deduplication.")
            unique_df = df

        logging.info("Deduplication completed successfully.")
        return unique_df

    except Exception as e:
        logging.error(f"Error deduplicating data: {e}")
        return df


# Example usage
if __name__ == "__main__":
    file_path = "C:\\Users\\fresh\\Documents\\Momo Card Settlement Project\\myenv\\data\\MOMORW_TRANSACTION_DUMP_20241031.csv"
    df = parse_csv(file_path, default_date='1970-01-01')
    if not df.empty:
        logging.info(f"Parsed DataFrame: {df.head()}")
    else:
        logging.error("Failed to parse the file.")