import os
import pandas as pd
import re
from datetime import datetime
from data_cleaning import clean_dataframe, clean_names, clean_dates, validate_date_of_birth, clean_addresses, validate_postcode, clean_phone_numbers, validate_email
from calculate_days_between import calculate_days_between

# Define folder containing CSV files
data_folder = r"C:\Users\Admin\Documents\library-quality-automation\Test_Data"
cleaned_folder = os.path.join(data_folder, "Cleaned")

# Ensure output folder exists
if not os.path.exists(cleaned_folder):
    os.makedirs(cleaned_folder)

# Get list of all CSV files in the directory
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

# Ask user if they want to invoke the days_between enhancement
invoke_days_between = input("Do you want to calculate 'days_between' for applicable files? (yes/no): ").strip().lower()

# Log file to track changes
log_file = os.path.join(cleaned_folder, "cleaning_log.txt")
with open(log_file, "w") as log:
    log.write("Data Cleaning Log\n=================\n\n")

    for file in csv_files:
        file_path = os.path.join(data_folder, file)
        try:
            # Load CSV file
            df = pd.read_csv(file_path, sep=",", quotechar='"', skipinitialspace=True, encoding="utf-8", engine="python")
            
            # Debugging: Print column names
            log.write(f"Processing file: {file}\n")
            log.write(f"Original Columns: {df.columns.tolist()}\n")
            
            # Apply Cleaning Functions
            df = clean_names(df)
            df = clean_dates(df)
            df = validate_date_of_birth(df)
            df = clean_addresses(df)
            df = validate_postcode(df)
            df = clean_phone_numbers(df)
            df = validate_email(df)
            df = clean_dataframe(df)
            
            # Conditionally invoke days_between enhancement
            if invoke_days_between == "yes":
                df = calculate_days_between(df)

            # Drop duplicate rows
            duplicate_count = df.duplicated().sum()
            df.drop_duplicates(inplace=True)
            log.write(f"Duplicates Removed: {duplicate_count}\n")

            # Handle missing values
            missing_count = df.isnull().sum().sum()
            df.fillna("Unknown", inplace=True)
            log.write(f"Missing Values Filled: {missing_count}\n")

            # Save cleaned file
            cleaned_file = os.path.join(cleaned_folder, f"cleaned_{file}")
            df.to_csv(cleaned_file, index=False)
            log.write(f"Cleaned file saved: {cleaned_file}\n\n")
            
        except Exception as e:
            log.write(f"Error processing {file}: {str(e)}\n\n")

print(f"Cleaning complete. Logs saved at: {log_file}")
