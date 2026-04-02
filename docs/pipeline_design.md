# Pipeline Design & Architecture

This document describes the end-to-end data flow from the Open-Meteo API to the Looker Studio dashboard.

## Conceptual Architecture

```mermaid
flowchart LR
    subgraph Data Sources
        API[Open-Meteo API]
    end

    subgraph Batch Layer (Local Machine)
        Extract[Python Extract]
        RawData[(/data/raw) CSV Storage]
        Transform[Pandas Transform]
        ProcessedData[(/data/processed) JSON/CSV]
    end

    subgraph Orchestration
        Airflow[Apache Airflow Scheduler]
        n8n[n8n Workflow Automation]
    end

    subgraph Load & Visualization
        GSheets[Google Sheets API]
        Looker[Google Looker Studio]
    end

    API --> Extract
    Extract --> RawData
    RawData --> Transform
    Transform --> ProcessedData
    ProcessedData --> GSheets
    GSheets --> Looker

    Airflow -- schedules --> Extract
    Airflow -- schedules --> Transform
    Airflow -- schedules --> GSheets
```

## Key Components

### 1. Extraction (Python)
- **Role:** Fetches daily weather data for a list of Indonesian cities (starting with Bandung).
- **Strategy:** Incremental loading. Each day, we fetch the 7-day forecast.
- **Fail-Safe:** Implements basic retry logic specifically for API timeouts/connectivity issues common in local home environments.

### 2. Transformation (Pandas/SQL)
- **Role:** Cleaning, normalization, and feature engineering.
- **Tasks:**
  - Standardizing timestamp formats.
  - Handling missing data in the API response.
  - Calculating "Rainy Day" flags based on precipitation thresholds.

### 3. Loading (Google Sheets API)
- **Role:** Acts as the "Reporting Ready" data store.
- **Why Google Sheets?** For small-to-medium datasets, it offers a zero-cost, cloud-accessible database that Looker Studio can query natively.

### 4. Orchestration (Airflow)
- **Role:** Managing dependencies and scheduling.
- **Frequency:** Daily at 01:00 AM (to ensure previous day's data is finalized).

## Design Pattern: "Write once, Read many"
The project is structured such that if the user wants to switch the target from **Google Sheets** to **BigQuery** or **Postgres**, they only need to modify the `load.py` script and the orchestration configuration. The core extraction and transformation logic remains decoupled.
