import os
import glob
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import re

# Configuration
SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'
SPREADSHEET_ID = 'https://docs.google.com/spreadsheets/d/1KAKNLiaPgo8InPhNL70Ea44H-b5QMk7eFzMnJvWqG_4/edit?gid=0#gid=0'  # User to replace in documentation
SHEET_NAME = 'Sheet1'  # Default sheet name for new Google Sheets
TRANSFORMED_DATA_PATH = "data/processed"

# Scopes for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def extract_spreadsheet_id(input_string):
    """Robustly extracts the Spreadsheet ID from a URL or raw ID string."""
    if "/d/" in input_string:
        # Match the ID between /d/ and the next / or end of string
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", input_string)
        if match:
            return match.group(1)
    # If not a URL, return the original string stripped of whitespace
    return input_string.strip()

def get_latest_processed_file():
    """Finds the most recent transformed CSV."""
    list_of_files = glob.glob(os.path.join(TRANSFORMED_DATA_PATH, "processed_weather_*.csv"))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def load_to_sheets(file_path):
    """Appends data from CSV to Google Sheets with deduplication."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: Credentials not found at {SERVICE_ACCOUNT_FILE}")
        return
        
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        # Extract the clean ID from the potentially messy config
        clean_spreadsheet_id = extract_spreadsheet_id(SPREADSHEET_ID)
        
        # 1. Verify sheet existence
        spreadsheet_meta = service.spreadsheets().get(spreadsheetId=clean_spreadsheet_id).execute()
        sheets = [s['properties']['title'] for s in spreadsheet_meta.get('sheets', [])]
        
        if SHEET_NAME not in sheets:
            print(f"Error: Sheet '{SHEET_NAME}' not found.")
            print(f"Available sheets: {', '.join(sheets)}")
            return

        # 2. Fetch existing dates from Column A for deduplication
        result = service.spreadsheets().values().get(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A:A"
        ).execute()
        
        existing_rows = result.get('values', [])
        # Extract existing dates (skipping headers or empty rows)
        existing_dates = set([row[0] for row in existing_rows if row])
        
        # 3. Filter the new dataframe
        df = pd.read_csv(file_path)
        df['date'] = df['date'].astype(str)
        
        new_data_df = df[~df['date'].isin(existing_dates)]
        
        if new_data_df.empty:
            print(f"No new records found. All dates in {os.path.basename(file_path)} already exist in Google Sheets.")
            return
            
        print(f"Found {len(new_data_df)} new records to append.")

        # 4. Prepare data for append
        # If the sheet is empty (excluding headers), add headers
        if not existing_rows:
            values = [new_data_df.columns.tolist()] + new_data_df.values.tolist()
        else:
            values = new_data_df.values.tolist()

        # 5. Execute Append
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A1",
            valueInputOption='USER_ENTERED', 
            body=body).execute()
        
        print(f"Success: {result.get('updates').get('updatedRows')} rows appended to '{SHEET_NAME}'.")
        
    except Exception as e:
        print(f"An error occurred while loading to Sheets: {e}")

def main():
    latest_file = get_latest_processed_file()
    if latest_file:
        print(f"Processing latest file: {latest_file}")
        load_to_sheets(latest_file)
    else:
        print("No processed data files (CSV) found in data/processed/")

if __name__ == "__main__":
    main()
