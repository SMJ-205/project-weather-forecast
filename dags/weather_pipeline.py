import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Resolve the absolute path to ensure the DAG works regardless of where Airflow starts
PROJECT_ROOT = "/Users/sarifmubdijantika/project-weather-forecast"
EXTRACT_SCRIPT = os.path.join(PROJECT_ROOT, "scripts/extract.py")
TRANSFORM_SCRIPT = os.path.join(PROJECT_ROOT, "scripts/transform.py")
LOAD_SCRIPT = os.path.join(PROJECT_ROOT, "scripts/load.py")

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'weather_forecast_pipeline_v1',
    default_args=default_args,
    description='ETL pipeline for weather data (Bandung & Indonesian cities)',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['weather', 'etl', 'portofolio'],
) as dag:

    # 1. Extraction Task
    t1_extract = BashOperator(
        task_id='extract_weather_data',
        bash_command=f'python3 {EXTRACT_SCRIPT}',
    )

    # 2. Transformation Task
    t2_transform = BashOperator(
        task_id='transform_weather_data',
        bash_command=f'python3 {TRANSFORM_SCRIPT}',
    )

    # 3. Load Task (Push to Google Sheets)
    t3_load = BashOperator(
        task_id='load_to_google_sheets',
        bash_command=f'python3 {LOAD_SCRIPT}',
    )

    # Setting task dependencies
    t1_extract >> t2_transform >> t3_load
