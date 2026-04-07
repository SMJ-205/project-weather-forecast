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
    """Overwrites Google Sheet with fresh dashboard data (NOW + 7 Days)."""
    # Handle credentials from file or environment variable (JSON string)
    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        info = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES)
    
    if not creds:
        print("Error: Google Credentials not found.")
        return
        
    try:
        service = build('sheets', 'v4', credentials=creds)
        clean_spreadsheet_id = extract_spreadsheet_id(SPREADSHEET_ID)
        
        # 1. Verify sheet existence
        spreadsheet_meta = service.spreadsheets().get(spreadsheetId=clean_spreadsheet_id).execute()
        sheets = [s['properties']['title'] for s in spreadsheet_meta.get('sheets', [])]
        
        if SHEET_NAME not in sheets:
            print(f"Error: Sheet '{SHEET_NAME}' not found.")
            return

        # 2. Clear existing data for a "Fresh Refresh" (No History)
        print(f"Clearing existing data in '{SHEET_NAME}' for fresh update...")
        service.spreadsheets().values().clear(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A:Z"
        ).execute()
        
        # 3. Prepare fresh data
        df = pd.read_csv(file_path)
        df = df.fillna("")
        
        # Include headers in the first row
        values = [df.columns.tolist()] + df.values.tolist()
            
        print(f"Loading {len(df)} forecast records (NOW + 7 Days)...")

        # 4. Execute Update (using A1 starting point)
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A1",
            valueInputOption='USER_ENTERED', 
            body=body).execute()
        
        print(f"Success: Dashboard updated for all Bandung regions.")
        
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
