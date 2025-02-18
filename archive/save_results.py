import os

def save_cleaned_data(df, filename, folder_path="Cleaned_Data"):
    """ Save cleaned DataFrame as a new CSV file """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    cleaned_filename = os.path.join(folder_path, f"cleaned_{filename}")
    df.to_csv(cleaned_filename, index=False)
    print(f" Cleaned file saved: {cleaned_filename}")
