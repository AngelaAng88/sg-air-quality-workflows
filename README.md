# sg-air-quality-workflows

Apache Airflow orchestration for the [sg-air-quality-etl](https://github.com/AngelaAng88/sg-air-quality-etl) pipeline. Runs the ETL daily at 12:30 AM SGT and loads Singapore air quality data into Google BigQuery.

---

## Overview

This repo contains the Airflow DAG and Docker Compose setup to schedule and run the `sg-air-quality-etl` pipeline. The ETL package is mounted from a local clone of the ETL repo and installed into the Airflow container at startup.

**Companion repo:** [sg-air-quality-etl](https://github.com/AngelaAng88/sg-air-quality-etl) — the ETL package this workflow depends on.

## Project Structure

```
sg-air-quality-workflows/
├── dags/
│   └── daily_air_quality_etl.py   # Airflow DAG — runs ETL daily at 12:30 AM SGT
├── docker-compose.yaml            # Airflow setup (init + webserver/scheduler)
├── .env.example                   # Environment variable template
├── .gitignore
└── README.md
```

## DAG: `daily_air_quality_etl`

| Property | Value |
|----------|-------|
| DAG ID | `daily_air_quality_etl` |
| Schedule | `30 0 * * *` (daily at 12:30 AM SGT) |
| Timezone | Asia/Singapore |
| Catchup | Disabled |
| Retries | 1 (5-minute delay) |

The DAG runs a single `PythonOperator` task that calls `run_etl_for_date()` from the ETL package, passing Airflow's `{{ ds }}` execution date (YYYY-MM-DD).

## Prerequisites

- Docker & Docker Compose
- A local clone of [sg-air-quality-etl](https://github.com/AngelaAng88/sg-air-quality-etl) with:
  - `.env` configured
  - `gcp-service-account.json` present in the repo root

## Setup

### 1. Clone this repository

```bash
git clone https://github.com/AngelaAng88/sg-air-quality-workflows.git
cd sg-air-quality-workflows
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Airflow
AIRFLOW__CORE__FERNET_KEY=your_fernet_key_here
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=your_password_here
AIRFLOW_ADMIN_EMAIL=your_email@example.com

# Absolute path to your local sg-air-quality-etl clone
ETL_PROJECT_PATH=/absolute/path/to/sg-air-quality-etl
```

To generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Start Airflow

```bash
docker-compose up -d
```

This runs two services:
- **`airflow-init`** — initialises the database and creates the admin user, then exits
- **`airflow`** — installs the ETL package, then starts the scheduler and webserver

Access the Airflow UI at `http://localhost:8080`.

### 4. Trigger the DAG

The `daily_air_quality_etl` DAG is enabled by default. It will run automatically on schedule, or you can trigger it manually from the Airflow UI.

## How It Works

At startup, the `airflow` container mounts the ETL repo from `ETL_PROJECT_PATH` and installs it as a Python package (`pip install -e`). The DAG then imports `run_etl_for_date()` directly from the package and calls it with the Airflow execution date.

Airflow logs are written to `./logs/` (gitignored). ETL output data (CSV) is written to `{ETL_PROJECT_PATH}/data/`.

## Related Repositories

| Repo | Description |
|------|-------------|
| [sg-air-quality-etl](https://github.com/AngelaAng88/sg-air-quality-etl) | ETL pipeline package (extract, transform, load) |
| sg-air-quality-workflows *(this repo)* | Airflow orchestration and scheduling |
