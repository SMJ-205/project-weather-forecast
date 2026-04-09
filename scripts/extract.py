import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# Configuration for Bandung Regions
CITIES = [
    {"name": "Bandung (Central)", "lat": -6.9175, "lon": 107.6191},
    {"name": "Bandung (North)", "lat": -6.85, "lon": 107.62},
    {"name": "Bandung (West)", "lat": -6.88, "lon": 107.54},
    {"name": "Bandung (East)", "lat": -6.92, "lon": 107.72},
    {"name": "Bandung (South)", "lat": -7.00, "lon": 107.60},
]

BASE_URL = "https://api.open-meteo.com/v1/forecast"
RAW_DATA_PATH = "data/raw"

def fetch_weather(city):
    """Fetches Current and Hourly weather data for dashboard."""
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "apparent_temperature", 
            "precipitation", 
            "rain", 
            "showers", 
            "weather_code", 
            "cloud_cover", 
            "wind_speed_10m"
        ],
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "apparent_temperature", 
            "precipitation", 
            "rain", 
            "showers", 
            "weather_code", 
            "cloud_cover", 
            "wind_speed_10m", 
            "uv_index", 
            "visibility"
        ],
        "timezone": "Asia/Jakarta",
        "past_days": 0,
        "forecast_days": 8
    }
    
    print(f"Fetching data for {city['name']}...")
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 1. Process Hourly
        hourly_df = pd.DataFrame(data['hourly'])
        hourly_df['data_type'] = 'Forecast'
        
        # 2. Process Current
        current_data = data['current']
        current_df = pd.DataFrame([current_data])
        current_df['data_type'] = 'Current'
        
        # Combine
        combined_df = pd.concat([current_df, hourly_df], ignore_index=True)
        
        combined_df['city'] = city['name']
        combined_df['latitude'] = city['lat']
        combined_df['longitude'] = city['lon']
        
        return combined_df
    except Exception as e:
        print(f"Error fetching data for {city['name']}: {e}")
        return None

def main():
    if not os.path.exists(RAW_DATA_PATH):
        os.makedirs(RAW_DATA_PATH)
        
    all_data = []
    for city in CITIES:
        df = fetch_weather(city)
        if df is not None:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(RAW_DATA_PATH, f"raw_weather_{timestamp}.csv")
        final_df.to_csv(output_file, index=False)
        print(f"Successfully saved raw data to {output_file}")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
