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
    """Appends data from CSV to Google Sheets."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: Credentials not found at {SERVICE_ACCOUNT_FILE}")
        return
        
    # Read the data
    df = pd.read_csv(file_path)
    # Convert dataframe to list of lists for Sheets API
    values = [df.columns.tolist()] + df.values.tolist() if is_sheet_empty() else df.values.tolist()

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        # Extract the clean ID from the potentially messy config
        clean_spreadsheet_id = extract_spreadsheet_id(SPREADSHEET_ID)
        
        # Call the Sheets API
        spreadsheet = service.spreadsheets().get(spreadsheetId=clean_spreadsheet_id).execute()
        sheets = [s['properties']['title'] for s in spreadsheet.get('sheets', [])]
        
        if SHEET_NAME not in sheets:
            print(f"Error: Sheet '{SHEET_NAME}' not found in spreadsheet.")
            print(f"Available sheets: {', '.join(sheets)}")
            print("Please create a sheet named 'Weather_Data' or update SHEET_NAME in the script.")
            return

        # Append data starting at the end of the current content
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=clean_spreadsheet_id, 
            range=f"{SHEET_NAME}!A1",
            valueInputOption='USER_ENTERED', 
            body=body).execute()
        
        print(f"{result.get('updates').get('updatedCells')} cells updated.")
        
    except Exception as e:
        print(f"An error occurred while loading to Sheets: {e}")

def is_sheet_empty():
    """Helper to check if sheet is empty to decide on headers."""
    # In a simplified portfolio version, we might skip this and always append without headers
    # or manage headers manually. For now, we append data only.
    return False 

def main():
    latest_file = get_latest_processed_file()
    if latest_file:
        print(f"Loading data from: {latest_file}")
        load_to_sheets(latest_file)
    else:
        print("No processed file found to load.")

if __name__ == "__main__":
    main()
