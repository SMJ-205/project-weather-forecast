import pandas as pd
import os
import glob
from datetime import datetime

# Transformation configuration
TRANSFORMED_DATA_PATH = "data/processed"
RAW_DATA_PATH = "data/raw"

def clean_and_transform(df):
    """Business logic for weather data transformation."""
    # Convert dates to proper objects
    df['time'] = pd.to_datetime(df['time'])
    
    # Feature Engineering: Precipitation Intensity
    def get_intensity(precip):
        if precip == 0: return "None"
        elif precip < 2.5: return "Light"
        elif precip < 10: return "Moderate"
        else: return "Heavy"
        
    df['rain_intensity'] = df['precipitation_sum'].apply(get_intensity)
    
    # Feature Engineering: Temperature Delta
    df['temp_delta'] = df['temperature_2m_max'] - df['temperature_2m_min']
    
    # Renaming for Clarity in Google Sheets/Looker
    df.rename(columns={
        'time': 'date',
        'temperature_2m_max': 'temp_max',
        'temperature_2m_min': 'temp_min',
        'precipitation_sum': 'precipitation',
        'wind_speed_10m_max': 'wind_max'
    }, inplace=True)
    
    # Sort by date and city
    df.sort_values(by=['city', 'date'], inplace=True)
    
    return df

def main():
    if not os.path.exists(TRANSFORMED_DATA_PATH):
        os.makedirs(TRANSFORMED_DATA_PATH)
        
    # Get the latest raw file
    raw_files = glob.glob(os.path.join(RAW_DATA_PATH, "raw_weather_*.csv"))
    if not raw_files:
        print("No raw data found to transform.")
        return
        
    latest_file = max(raw_files, key=os.path.getctime)
    print(f"Transforming latest raw data: {latest_file}")
    
    df = pd.read_csv(latest_file)
    transformed_df = clean_and_transform(df)
    
    # Save processed backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(TRANSFORMED_DATA_PATH, f"processed_weather_{timestamp}.csv")
    transformed_df.to_csv(output_file, index=False)
    
    print(f"Successfully transformed data and saved to {output_file}")
    print(transformed_df.head())

if __name__ == "__main__":
    main()
