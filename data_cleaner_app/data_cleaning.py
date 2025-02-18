import pandas as pd
import re
from datetime import datetime

def detect_column(df, possible_names):
    """Detects and returns the first matching column from a list of possible names."""
    return next((col for col in possible_names if col in df.columns), None)

def clean_names(df):
    """Cleans and standardizes names by removing special characters and capitalizing properly."""
    name_columns = ["Full Name", "First Name", "Last Name", "Given Name", "Surname"]

    def format_name(name):
        if pd.isna(name) or name == "Unknown":
            return "Unknown"
        # remove non-alpha, then title case
        cleaned = re.sub(r"[^a-zA-Z\s]", "", str(name))
        return cleaned.title().strip()

    for col in name_columns:
        if col in df.columns:
            df[col] = df[col].apply(format_name)

    return df

def clean_addresses(df):
    """Standardizes addresses by stripping whitespace and capitalizing."""
    address_columns = ["Address", "Street Address", "Home Address", "Postal Address"]
    for col in address_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df

def validate_postcode(df):
    """Detects and validates postcode columns dynamically."""
    possible_postcodes = ["Postcode", "Post Code", "Postal Code", "ZIP", "Zip Code"]
    postcode_col = detect_column(df, possible_postcodes)

    if postcode_col:
        df[postcode_col] = df[postcode_col].astype(str).str.upper().str.strip()
        uk_pattern = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$")
        df["Valid Postcode"] = df[postcode_col].apply(
            lambda x: "Valid" if uk_pattern.match(x) else "Invalid"
        )
    return df

def clean_phone_numbers(df):
    """Detects and cleans phone number columns dynamically."""
    phone_cols = ["Phone", "Phone Number", "Mobile", "Contact No", "Tel", "telephone"]
    phone_col = detect_column(df, phone_cols)

    if phone_col:
        pattern = re.compile(r"^\+?\d{10,15}$")
        df[phone_col] = df[phone_col].astype(str).apply(
            lambda x: x if pattern.match(x) else "Invalid"
        )
    return df

def validate_email(df):
    """Detects and validates email columns dynamically."""
    email_cols = ["Email", "E-mail", "Email Address"]
    email_col = detect_column(df, email_cols)

    if email_col:
        pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]+$")
        df[email_col] = df[email_col].astype(str).apply(
            lambda x: x if pattern.match(x) else "Invalid"
        )
    return df

def clean_dates(df):
    """
    Convert recognized date columns (DD/MM/YYYY) to datetime.
    Unrecognized formats remain as original strings.
    """
    date_columns = [
        "Date of Birth",
        "DOB",
        "Birth Date",
        "Join Date",
        "Registration Date",
        "Book checkout",
        "Book Returned",
    ]

    for col in date_columns:
        if col in df.columns:
            # strip extraneous triple quotes if any
            df[col] = df[col].astype(str).str.replace('"""', '"')
            df[col] = df[col].str.strip('"')

            # basic check for DD/MM/YYYY
            valid_mask = df[col].str.match(r"^\d{1,2}/\d{1,2}/\d{4}$")
            parsed = pd.to_datetime(df.loc[valid_mask, col], format="%d/%m/%Y", errors="coerce")

            # only replace those that matched
            df.loc[valid_mask, col] = parsed
    return df

def validate_date_of_birth(df):
    """
    Ensures date of birth is within a valid range (1 to 120 years old).
    If out of range or invalid, sets to NaT.
    """
    dob_col = detect_column(df, ["Date of Birth", "DOB", "Birth Date"])

    if dob_col:
        # re-parse everything that might be a date
        valid_mask = df[dob_col].astype(str).str.match(r"^\d{1,2}/\d{1,2}/\d{4}$")
        parsed = pd.to_datetime(df.loc[valid_mask, dob_col], format="%d/%m/%Y", errors='coerce')
        df.loc[valid_mask, dob_col] = parsed

        # calculate age
        current_year = datetime.now().year
        df["Age"] = current_year - pd.to_datetime(df[dob_col], errors='coerce').dt.year
        df.loc[(df["Age"] < 1) | (df["Age"] > 120), dob_col] = pd.NaT
        df.drop(columns=["Age"], inplace=True)

    return df

def clean_dataframe(df):
    """Master function that applies all cleaning & validation steps."""
    # 1) Names, addresses, phone, email, postcode
    df = clean_names(df)
    df = clean_addresses(df)
    df = validate_postcode(df)
    df = clean_phone_numbers(df)
    df = validate_email(df)

    # 2) Dates
    df = clean_dates(df)
    df = validate_date_of_birth(df)

    # 3) Remove duplicates
    df.drop_duplicates(inplace=True)

    # 4) Properly fill missing values
    # numeric
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = df[col].fillna(0)
    # datetime
    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].fillna(pd.NaT)
    # string
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("Unknown")

    return df
