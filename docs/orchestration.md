# Orchestration: Airflow & n8n

This document explains the choices and setup for the pipeline's orchestration layer, specifically tailored for **MacBook M1/M2** environments.

## Choosing the Right Orchestrator

This project showcases two potential paths for scheduling:

| Aspect | Apache Airflow | n8n (Alternative) |
|---|---|---|
| **Best For** | Complex ETL, Python DAGs | Low-code automation, Rapid Prototyping |
| **Logic** | Code-Defined (DAGs) | Visual Node Canvas |
| **Local Setup** | Moderate (Python envs) | Low (Docker/npm) |
| **Recruiter Appeal** | High (Industry Standard) | Moderate (Automation Specialist) |

## Standard Environment (macOS M1)

### 🚨 Prerequisites
1. **Homebrew:** `curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh`
2. **Python:** `brew install python@3.11`
3. **Airflow Constraints:** Using the official constraints file to ensure stability on ARM architecture.

### Setting Up Apache Airflow (Standalone)
For this portfolio project, we use the `standalone` mode for simplicity and zero-cost local metadata storage (SQLite).

```bash
# 1. Define Airflow Home
export AIRFLOW_HOME=~/airflow_project

# 2. Install Airflow with specific constraints
pip install "apache-airflow==2.10.x" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.x/constraints-3.11.txt"

# 3. Initialize & Start
airflow standalone
```
*Wait for the `standalone_admin_password.txt` file to be generated in your project folder.*

### Scheduling the Weather DAG
- Locate the `dags/` folder in this repository.
- Symbolically link it to your Airflow home:
  `ln -s $(pwd)/dags $AIRFLOW_HOME/dags`
- Refresh the Airflow UI at `http://localhost:8080`.

## n8n (Optional Low-Code Path)
If you prefer visual orchestration, an `n8n_workflow.json` is included in the project root.
1. Run `n8n` locally via npm: `npx n8n`.
2. Import the JSON workflow from this repo.
3. Configure the HTTP node and Google Sheets node as per the diagram.
