# Transformation Logic: Data Cleaning & Feature Engineering

This document details the transformation step within the ETL pipeline, implemented using **Python (Pandas)**.

## Core Transformation Steps

### 1. JSON-to-Flattened Structure
Raw responses from Open-Meteo contain nested JSON payloads with separate "daily" keys for dates, temperatures, and precipitation.
- **Action:** Convert these into a tabular format where each row represents a unique `(date, latitude, longitude)` tuple.

### 2. Temporal Normalization
API responses often use millisecond timestamps or ISO strings.
- **Action:** Convert all time-related fields to a consistent `YYYY-MM-DD` format.
- **Rationale:** Simplifies joins with other datasets and ensures Looker Studio recognizes the `Date` dimension correctly.

### 3. Derived Features (Feature Engineering)
To provide more descriptive insights beyond raw numbers, we calculate the following:

- **`rain_intensity`**: Categorizes daily precipitation sum into:
  - `None`: 0mm
  - `Light`: < 2.5mm
  - `Moderate`: 2.5mm - 10mm
  - `Heavy`: > 10mm
- **`temp_delta`**: The difference between the daily maximum and minimum temperatures (`temperature_2m_max` - `temperature_2m_min`).

## Data Validation Layer
Before loading data into Google Sheets, the script performs a "Sanity Check":
- **Constraint:** `temperature_2m_max` > `temperature_2m_min`.
- **Constraint:** `precipitation_sum` >= 0.
- **Action:** Any invalid data rows are logged and quarantined in `/data/quarantine/` for manual inspection, ensuring only clean data reaches the dashboard.

## Output Format
The resulting dataset is saved as a **Standardized CSV** for local backup and then pushed to **Google Sheets** via the `google-api-python-client`.
