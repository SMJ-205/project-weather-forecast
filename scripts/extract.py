import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# Configuration for Bandung and other cities
CITIES = [
    {"name": "Bandung", "lat": -6.9175, "lon": 107.6191},
    # Add more cities here as needed:
    # {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456},
    # {"name": "Surabaya", "lat": -7.2575, "lon": 112.7521},
]

BASE_URL = "https://api.open-meteo.com/v1/forecast"
RAW_DATA_PATH = "data/raw"

def fetch_weather(city):
    """Fetches hourly weather data for a given city (focusing on rain/radar)."""
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": ["precipitation", "rain", "showers", "weather_code", "temperature_2m"],
        "timezone": "Asia/Jakarta",
        "past_days": 1,
        "forecast_days": 1
    }
    
    print(f"Fetching hourly data for {city['name']}...")
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Flattening the nested JSON 'hourly' key
        df = pd.DataFrame(data['hourly'])
        df['city'] = city['name']
        df['latitude'] = city['lat']
        df['longitude'] = city['lon']
        
        return df
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
