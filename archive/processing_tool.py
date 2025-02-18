import pandas as pd
import re
from datetime import datetime

def detect_column(df, possible_names):
    """Detects and returns the first matching column from a list of possible names."""
    return next((col for col in possible_names if col in df.columns), None)

def clean_dates(df):
    """Convert detected date columns to datetime format."""
    date_columns = ["Date of Birth", "DOB", "Birth Date", "Join Date", "Registration Date", "Book checkout", "Book Returned"]

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('"""', '"').str.strip('"')
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

    return df

def validate_date_of_birth(df):
    """Ensures date of birth is within a valid range (18 to 120 years old)."""
    dob_column = detect_column(df, ["Date of Birth", "DOB", "Birth Date"])
    if dob_column:
        df[dob_column] = pd.to_datetime(df[dob_column], errors='coerce')
        current_year = datetime.now().year
        df["Age"] = current_year - df[dob_column].dt.year
        df.loc[(df["Age"] < 18) | (df["Age"] > 120), dob_column] = pd.NaT
        df.drop(columns=["Age"], inplace=True)
    return df

def clean_names(df):
    """Standardizes names by removing special characters and capitalizing correctly."""
    name_columns = ["Full Name", "First Name", "Last Name", "Given Name", "Surname"]

    def format_name(name):
        if pd.isna(name) or name == "Unknown":
            return "Unknown"
        clean_name = re.sub(r"[^a-zA-Z\s]", "", name)
        return clean_name.title().strip()

    for col in name_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(format_name)
    return df

def clean_addresses(df):
    """Standardizes address fields by removing leading/trailing spaces and capitalizing."""
    address_columns = ["Address", "Street Address", "Home Address", "Postal Address"]
    for col in address_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df

def validate_postcode(df):
    """Detects and validates postcode columns dynamically."""
    postcode_column = detect_column(df, ["Postcode", "Post Code", "Postal Code", "ZIP", "Zip Code"])
    if postcode_column:
        df[postcode_column] = df[postcode_column].astype(str).str.upper().str.strip()
        uk_postcode_pattern = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$")
        df["Valid Postcode"] = df[postcode_column].apply(lambda x: "Valid" if uk_postcode_pattern.match(x) else "Invalid")
    return df

def clean_phone_numbers(df):
    """Detects and cleans phone number columns dynamically."""
    phone_column = detect_column(df, ["Phone", "Phone Number", "Mobile", "Contact No", "Tel", "telephone"])
    if phone_column:
        pattern = re.compile(r"^\+?\d{10,15}$")
        df[phone_column] = df[phone_column].astype(str).apply(lambda x: x if pattern.match(str(x)) else "Invalid")
    return df

def validate_email(df):
    """Detects and validates email columns dynamically."""
    email_column = detect_column(df, ["Email", "E-mail", "Email Address"])
    if email_column:
        pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        df[email_column] = df[email_column].astype(str).apply(lambda x: x if pattern.match(str(x)) else "Invalid")
    return df

def clean_dataframe(df):
    """Cleans the entire DataFrame by applying multiple validation and formatting steps."""
    df = clean_names(df)
    df = clean_dates(df)
    df = validate_date_of_birth(df)
    df = clean_addresses(df)
    df = validate_postcode(df)
    df = clean_phone_numbers(df)
    df = validate_email(df)
    df.drop_duplicates(inplace=True)
    df.fillna("Unknown", inplace=True)
    return df
