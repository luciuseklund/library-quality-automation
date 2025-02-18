import pandas as pd
import os

def load_csv():
    choice = input("Do you want to process a single file (1) or all files in a folder (2)? ")

    if choice == "1":
        filename = input("Enter the CSV filename (including .csv extension): ")
        if not os.path.exists(filename):
            print(f" File '{filename}' not found!")
            return None
        df = pd.read_csv(filename)
        print(f" Loaded {filename}")
        return df, filename

    elif choice == "2":
        folder_path = "Test_Data"
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        if not csv_files:
            print(" No CSV files found in the folder.")
            return None
        
        print(f" Found {len(csv_files)} CSV files: {csv_files}")

        dataframes = {}
        for file in csv_files:
            file_path = os.path.join(folder_path, file)
            dataframes[file] = pd.read_csv(file_path)
        
        return dataframes, folder_path

    else:
        print(" Invalid choice! Enter '1' or '2'.")
        return None
