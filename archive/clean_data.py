import pandas as pd
import re
from datetime import datetime

def clean_dataframe(df):
    """ Perform cleaning: remove duplicates, fill missing values, validate data """
    
    # Fill missing values
    for column in df.columns:
        if df[column].dtype == "float64" or df[column].dtype == "int64":
            df[column].fillna(0, inplace=True)
        else:
            df[column].fillna("Unknown", inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    return df

def detect_column(df, possible_names):
    """Detects and returns the first matching column from a list of possible names."""
    return next((col for col in possible_names if col in df.columns), None)

def clean_dates(df):
    """
    Convert date columns to datetime format.
    Detects common date column names automatically.
    """
    date_columns = ["Date of Birth", "DOB", "Birth Date", "Join Date", "Registration Date", "date_of_birth"]

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip('"')  # Remove surrounding quotes
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)  # Convert to datetime (DD/MM/YYYY format)

    return df

def validate_date_of_birth(df):
    """
    Ensures date of birth:
    - Falls within a realistic range (18 to 120 years old)
    - Converts invalid dates to NaT
    """
    dob_column = detect_column(df, ["Date of Birth", "DOB", "Birth Date", "date_of_birth"])

    if dob_column:
        df[dob_column] = pd.to_datetime(df[dob_column], errors='coerce')

        # Calculate age and filter out unrealistic values
        current_year = datetime.now().year
        df["Age"] = current_year - df[dob_column].dt.year
        df.loc[(df["Age"] < 1) | (df["Age"] > 120), dob_column] = pd.NaT
        df.drop(columns=["Age"], inplace=True)  # Remove temporary age column

    return df

def clean_names(df):
    """
    Ensures names are properly formatted:
    - Removes numbers & special characters
    - Capitalizes first letter of each word
    """
    name_columns = ["Full Name", "First Name", "Last Name", "Given Name", "Surname", "full_name"]

    def format_name(name):
        if pd.isna(name) or name == "Unknown":
            return "Unknown"
        clean_name = re.sub(r"[^a-zA-Z\s]", "", name)  # Remove non-alpha characters
        return clean_name.title().strip()  # Capitalize and remove leading/trailing spaces

    for col in name_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(format_name)

    return df

def clean_addresses(df):
    """
    Cleans address fields:
    - Removes leading/trailing spaces
    - Capitalizes first letter of each word
    """
    address_columns = ["Address", "Street Address", "Home Address", "Postal Address"]

    for col in address_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df

def validate_postcode(df):
    """
    Detects and validates postcode columns dynamically.
    """
    postcode_column = detect_column(df, ["Postcode", "Post Code", "Postal Code", "postcode"])

    if postcode_column:
        uk_postcode_pattern = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$")
        df[postcode_column] = df[postcode_column].astype(str).str.upper().str.strip()
        df["Valid Postcode"] = df[postcode_column].apply(lambda x: "Valid" if uk_postcode_pattern.match(x) else "Invalid")

    return df

def clean_phone_numbers(df):
    """
    Detects and cleans phone number columns dynamically.
    """
    phone_column = detect_column(df, ["Phone", "Phone Number", "Mobile", "Contact No", "Tel", "telephone"])

    if phone_column:
        pattern = re.compile(r"^\+?\d{10,15}$")
        df[phone_column] = df[phone_column].astype(str).apply(lambda x: x if pattern.match(str(x)) else "Invalid")

    return df

def validate_email(df):
    """
    Detects and validates email columns dynamically.
    """
    email_column = detect_column(df, ["Email", "E-mail", "Email Address", "email"])

    if email_column:
        pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        df[email_column] = df[email_column].astype(str).apply(lambda x: x if pattern.match(str(x)) else "Invalid")

    return df

