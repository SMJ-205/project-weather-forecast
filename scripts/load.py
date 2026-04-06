import os
import glob
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import re

# Configuration
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials/service_account.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1KAKNLiaPgo8InPhNL70Ea44H-b5QMk7eFzMnJvWqG_4') 
SHEET_NAME = 'Sheet1'
TRANSFORMED_DATA_PATH = "data/processed"

# Scopes for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def extract_spreadsheet_id(input_string):
    """Robustly extracts the Spreadsheet ID from a URL or raw ID string."""
    if "/d/" in input_string:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", input_string)
        if match:
            return match.group(1)
    return input_string.strip()

def get_latest_processed_file():
    """Finds the most recent transformed CSV."""
    list_of_files = glob.glob(os.path.join(TRANSFORMED_DATA_PATH, "processed_weather_*.csv"))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def load_to_sheets(file_path):
    """Appends data from CSV to Google Sheets with hourly deduplication."""
    # Handle credentials from file or environment variable (JSON string)
    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        # For GitHub Actions where we might pass the JSON string directly
        info = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES)
    
    if not creds:
        print("Error: Google Credentials not found (checked file and environment).")
        return
        
    try:
        service = build('sheets', 'v4', credentials=creds)
        clean_spreadsheet_id = extract_spreadsheet_id(SPREADSHEET_ID)
        
        # 1. Verify sheet existence
        spreadsheet_meta = service.spreadsheets().get(spreadsheetId=clean_spreadsheet_id).execute()
        sheets = [s['properties']['title'] for s in spreadsheet_meta.get('sheets', [])]
        
        if SHEET_NAME not in sheets:
            print(f"Error: Sheet '{SHEET_NAME}' not found. Available: {', '.join(sheets)}")
            return

        # 2. Fetch existing timestamps for deduplication
        # Assuming timestamp is in Column A
        result = service.spreadsheets().values().get(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A:A"
        ).execute()
        
        existing_rows = result.get('values', [])
        existing_timestamps = set([row[0] for row in existing_rows if row])
        
        # 3. Filter the new dataframe
        df = pd.read_csv(file_path)
        # Handle renaming of 'date' to 'timestamp' in previous transformation
        timestamp_col = 'timestamp' if 'timestamp' in df.columns else 'date'
        df[timestamp_col] = df[timestamp_col].astype(str)
        
        new_data_df = df[~df[timestamp_col].isin(existing_timestamps)]
        
        if new_data_df.empty:
            print(f"No new hourly records found. All timestamps already exist in Google Sheets.")
            return
            
        print(f"Found {len(new_data_df)} new records to append.")

        # 4. Prepare data for append
        # Fill NaN values with empty string to avoid JSON errors with Google API
        new_data_df = new_data_df.fillna("")
        
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
        
        print(f"Success: {result.get('updates').get('updatedRows')} rows appended.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    latest_file = get_latest_processed_file()
    if latest_file:
        print(f"Processing: {latest_file}")
        load_to_sheets(latest_file)
    else:
        print("No processed data files found.")

if __name__ == "__main__":
    main()
