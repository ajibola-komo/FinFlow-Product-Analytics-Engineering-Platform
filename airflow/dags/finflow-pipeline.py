from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime


def generate_data():
    print("Generating FinFlow synthetic data...")


def load_to_data_lake():
    print("Loading data to GCS...")


def load_to_warehouse():
    print("Loading data to Snowflake...")


with DAG(
    dag_id="finflow_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    generate_task = PythonOperator(
        task_id="generate_data",
        python_callable=generate_data,
    )

    load_task = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=load_to_warehouse,
    )

    generate_task >> load_task
