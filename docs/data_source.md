# Data Source: Open-Meteo API

This project utilizes the **Open-Meteo Free Weather API** to retrieve historical and forecast weather data for **Bandung, Indonesia** and surrounding regions.

## API Overview
- **Provider:** [Open-Meteo](https://open-meteo.com)
- **License:** Attribution 4.0 International (CC BY 4.0)
- **Authentication:** No API Key required (suitable for local/dev/portfolio use).
- **Core Endpoint:** `https://api.open-meteo.com/v1/forecast`

## Target Location (Bandung)
- **Latitude:** -6.9175
- **Longitude:** 107.6191
- **Timezone:** Asia/Jakarta (GMT+7)

## Data Contract: Daily Weather Attributes
Each extraction job targets a specific set of attributes required for trend analysis:

| Field Name | Type | Description | Unit |
|---|---|---|---|
| `date` | String (ISO) | Forecast/Measurement date | YYYY-MM-DD |
| `temperature_2m_max` | Float | Maximum temperature at 2m height | °C |
| `temperature_2m_min` | Float | Minimum temperature at 2m height | °C |
| `precipitation_sum` | Float | Total daily precipitation | mm |
| `wind_speed_10m_max`| Float | Max wind gusts recorded | km/h |

## Scalability
The extraction script is designed with a **Dynamic City Configuration**. By passing a list of Lat/Lon coordinates (e.g., Jakarta, Surabaya, Yogyakarta), the pipeline can iterate through all major Indonesian cities and append the data to the central target.

## Rate Limiting Assumptions
- The API is rate-limited to 10,000 requests per day.
- For this portfolio project, we schedule a single batch request per day (at 00:00 UTC) to fetch the 7-day forecast.
