from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
from sg_air_quality.main import run_etl_for_date
import pendulum

local_tz = pendulum.timezone("Asia/Singapore")

default_args = {
    "owner": "Angela Ang",
    "start_date": days_ago(0),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_daily_etl(execution_date: str, **context):
    """
    Wrapper for Airflow to call the ETL.
    Airflow passes execution_date as YYYY-MM-DD.
    """
    run_etl_for_date(input_date=execution_date)

with DAG(
    dag_id="daily_air_quality_etl",
    description="Daily ETL for Singapore air quality data",
    default_args=default_args,
    schedule="30 0 * * *",  # daily at 12:30 AM
    start_date=pendulum.datetime(2026, 1, 1, tz=local_tz),
    catchup=False,
    tags=["air-quality", "etl", "portfolio"],
) as dag:

    etl_task = PythonOperator(
        task_id="run_daily_air_quality_etl",
        python_callable=run_daily_etl,
        op_kwargs={
            # Airflow macro → execution date as YYYY-MM-DD
            "execution_date": "{{ ds }}",
        },
    )

    etl_task
