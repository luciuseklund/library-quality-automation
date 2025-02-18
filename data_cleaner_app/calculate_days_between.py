import pandas as pd
from datetime import datetime

def calculate_days_between(df):
    """Calculate days between 'Book checkout' and 'Book Returned' and add as a new column."""
    if 'Book checkout' in df.columns and 'Book Returned' in df.columns:
        df['Book checkout'] = pd.to_datetime(df['Book checkout'], errors='coerce')
        df['Book Returned'] = pd.to_datetime(df['Book Returned'], errors='coerce')
        df['days_between'] = (df['Book Returned'] - df['Book checkout']).dt.days
    else:
        print("Required columns for date calculation are missing.")
    return df