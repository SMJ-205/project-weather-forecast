# Visualization: Looker Studio & Google Sheets

This documentation explains the data-to-dashboard connection for the Weather Forecast Pipeline.

## Connecting Data to Looker Studio

For this portfolio project, we use **Google Sheets** as a "Zero-Cost Warehouse" to feed **Google Looker Studio**.

### 1. Step: Set Up Source Sheet & API
- Create a new Google Sheet named `Weather_Dashboard_Data`.
- Define headers in the first row matching the processed CSV: `date`, `city`, `latitude`, `longitude`, `temp_max`, `temp_min`, `precipitation`, `wind_max`, `rain_intensity`, `temp_delta`.
- **Spreadsheet ID:** Copy the long string in your sheet's URL (between `/d/` and `/edit`). Open `scripts/load.py` and replace `YOUR_SPREADSHEET_ID_HERE` with this value.

### 2. Step: OAuth Credentials
- Create a directory named `credentials/` in the project root.
- Place your Google Cloud Service Account JSON file inside and rename it to `service_account.json`. (This file is ignored by `.gitignore` for security).
- **Action:** Share the Target Google Sheet with the `client_email` found in your service account JSON file (Editor permissions).

### 3. Step: Connect Looker Studio
1. Open [Looker Studio](https://lookerstudio.google.com).
2. Click **Create** -> **Data Source**.
3. Select **Google Sheets** connector.
4. Pick Your `Weather_Dashboard_Data` spreadsheet.
5. Ensure the `date` field is typed as **Date (YYYYMMDD)** in Looker's setup.

## Visual Insights (Recommended)

To demonstrate advanced data storytelling, the dashboard should include:

- **Temperature Trends (Time Series):** Line chart showing `temp_max` vs `temp_min` over time.
- **Precipitation Analysis (Bar Chart):** Daily `precipitation` sum to monitor rainy seasons.
- **Regional Heatmap:** An interactive map of Indonesia showing forecast temperatures by coordinate.
- **KPI Cards:** Displaying "Highest Expected Temp" and "Total Weekly Rainfall" for Bandung.

## Alternative: BigQuery Sandbox
For an enterprise-grade experience (SQL-based), you can switch the target to **BigQuery**. Looker Studio's BigQuery connector is highly optimized for performance and large-scale datasets, and the [BigQuery Sandbox](https://cloud.google.com/bigquery/docs/sandbox) provides 10GB of free storage.
