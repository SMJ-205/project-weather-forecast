import pandas as pd
import os
import glob
from datetime import datetime

# Transformation configuration
TRANSFORMED_DATA_PATH = "data/processed"
RAW_DATA_PATH = "data/raw"

def clean_and_transform(df):
    """Business logic for weather data transformation (Hourly)."""
    # Convert dates/times to proper objects
    df['time'] = pd.to_datetime(df['time'])
    
    # Weather Code Mapping (WMO codes)
    WMO_CODES = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    df['weather_desc'] = df['weather_code'].map(WMO_CODES).fillna("Unknown")
    
    # Feature Engineering: Hourly Rain Intensity
    def get_intensity(precip):
        if precip == 0: return "None"
        elif precip < 2.5: return "Light"
        elif precip < 7.6: return "Moderate"
        else: return "Heavy"
        
    df['rain_intensity'] = df['precipitation'].apply(get_intensity)
    
    # Renaming for Clarity in Dashboard
    df.rename(columns={
        'time': 'timestamp',
        'temperature_2m': 'temp_c',
        'apparent_temperature': 'feels_like_c',
        'relative_humidity_2m': 'humidity_pct',
        'precipitation': 'precip_mm',
        'rain': 'rain_mm',
        'showers': 'showers_mm',
        'wind_speed_10m': 'wind_kmh',
        'cloud_cover': 'cloud_pct',
        'visibility': 'visibility_m'
    }, inplace=True)
    
    # Sort: Current first, then Forecast by timestamp
    df.sort_values(by=['city', 'data_type', 'timestamp'], ascending=[True, True, True], inplace=True)
    
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
