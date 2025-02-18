import pandas as pd
import re
from datetime import datetime

# Define file path
file_path = r"C:\Users\Admin\Documents\library-quality-automation\Test_Data\03_Library Systembook.csv"

# Read CSV file
df = pd.read_csv(file_path, sep=",", quotechar='"', skipinitialspace=True, encoding="utf-8", engine="python")

# Function to clean up date fields
def clean_date(value):
    """Removes extra triple quotes and converts to a proper date format."""
    if isinstance(value, str):
        value = value.replace('"""', '"').strip('"')  # Remove extra quotes
        try:
            return pd.to_datetime(value, format="%d/%m/%Y", errors="coerce")  # Convert to datetime
        except ValueError:
            return pd.NaT  # Mark invalid dates as NaT
    return pd.NaT  # If value is not a string, return NaT

# Apply date cleaning to relevant columns
date_columns = ["Book checkout", "Book Returned"]
for col in date_columns:
    if col in df.columns:
        df[col] = df[col].apply(clean_date)

# Remove completely empty rows
df.dropna(how="all", inplace=True)

# Identify invalid dates (e.g., 32nd May or years far in the future)
for col in date_columns:
    if col in df.columns:
        df.loc[df[col] > datetime.now(), col] = pd.NaT  # Remove dates in the future
        df.loc[df[col].dt.day > 31, col] = pd.NaT  # Remove impossible day values

# Handle missing values
df.fillna({"Books": "Unknown", "Customer ID": "Unknown"}, inplace=True)

# Save cleaned data
cleaned_file_path = r"C:\Users\Admin\Documents\library-quality-automation\Test_Data\cleaned_books.csv"
df.to_csv(cleaned_file_path, index=False)

print(f" Cleaned data saved at: {cleaned_file_path}")
