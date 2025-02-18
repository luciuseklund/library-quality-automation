import pandas as pd
import re
from datetime import datetime
from sqlalchemy import create_engine
import pyodbc

# Database connection details
server = 'localhost'
database = 'BACKM_DE5M5'
username = 'PY-USER'
password = 'pass123'

#  connection string

connection_string = f'mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'


engine = create_engine(connection_string)

# --- Cleaning Functions ---
def clean_names(df):
    
    if 'Customer Name' in df.columns:
        df['Customer Name'] = df['Customer Name'].astype(str).str.replace(r"[^a-zA-Z\s]", "", regex=True).str.title().str.strip()
    return df

def clean_addresses(df):
  
    address_columns = ["Address", "Street", "City"]
    for col in address_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title().str.strip()
    return df

def validate_postcode(df):

    if 'Postcode' in df.columns:
        df['Postcode'] = df['Postcode'].astype(str).str.upper().str.replace(" ", "")
    return df

def clean_phone_numbers(df):

    if 'Phone' in df.columns:
        df['Phone'] = df['Phone'].astype(str).str.replace(r"[^\d]", "", regex=True)
    return df

def validate_email(df):

    if 'Email' in df.columns:
        df['Email'] = df['Email'].astype(str).apply(lambda x: x.lower() if re.match(r"[^@]+@[^@]+\.[^@]+", x) else "Invalid")
    return df

def clean_dates(df):
    """Convert date columns to datetime and strip surrounding quotes."""
    date_columns = ["Book checkout", "Book Returned"]
    
    for col in date_columns:
        if col in df.columns:
            # Ensure values are treated as strings and strip quotes before converting to datetime
            df[col] = df[col].astype(str).str.strip('"')  # Remove double quotes
            df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime
            
    return df


def validate_date_of_birth(df):

    if 'Date of Birth' in df.columns:
        df['Date of Birth'] = pd.to_datetime(df['Date of Birth'], errors='coerce')
    return df

# --- Main Cleaning Function ---
def clean_dataframe(df):
    df = clean_names(df)
    df = clean_addresses(df)
    df = validate_postcode(df)
    df = clean_phone_numbers(df)
    df = validate_email(df)
    df = clean_dates(df)
    df = validate_date_of_birth(df)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Handle missing values
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = df[col].fillna(0)
    
    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].fillna(pd.NaT)
    
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("Unknown")

    return df

# --- SQL Import Function ---
def insert_to_sql(df, table_name):

    for col in df.select_dtypes(include=['datetime64']):
        df[col] = df[col].astype(str)  # Convert datetime to string

    try:
        df.to_sql(table_name, con=engine, schema='dbo', if_exists='replace', index=False)
        print(f"Data successfully inserted into {table_name} in SQL Server!")
    except Exception as e:
        print(f"SQL Insert Error: {e}")
