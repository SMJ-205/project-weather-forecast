# Assumptions & Project Constraints

This document clarifies the design decisions and environmental limits of this portfolio project.

## 1. Local-First Environment
- **Assumption:** The pipeline runs on a **MacBook Air M1/M2**.
- **Constraint:** No cloud hosting (AWS/GCP VMs) is utilized.
- **Impact:** Airflow scheduler must be manually started via `airflow standalone` during the demonstration or for scheduled runs.

## 2. API Usage
- **Assumption:** Open-Meteo's free tier remains accessible.
- **Constraint:** No API key is required, reducing setup friction for reviewers.
- **Design:** The code handles HTTP 429 (Too Many Requests) with exponential backoff.

## 3. Storage Strategy
- **Assumption:** Dataset remains small (forecast data < 10MB per year).
- **Constraint:** Google Sheets is the target.
- **Impact:** We append fresh forecast data to a single sheet. For historical analysis (> 5 million cells), shifting to BigQuery would be recommended.

## 4. Cost Zero Policy
- **Assumption:** The user wants zero financial overhead.
- **Constraint:** All tools (Python, Airflow, Google Sheets, Looker Studio) are free or have generous free/sandbox tiers.

## 5. Scalability
- **Assumption:** Future expansion to other cities (Jakarta, Surabaya, etc.) will follow the same data schema.
- **Design:** The `extract.py` script is parameterized for coordinate lists.
