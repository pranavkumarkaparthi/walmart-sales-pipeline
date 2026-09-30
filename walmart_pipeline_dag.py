from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="walmart_pipeline",
    start_date=datetime(2026, 9, 30),
    schedule="@daily",
    catchup=False,
    tags=["walmart"],
) as dag:

    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command='cd "/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline" && python3 my_pipeline_postgres.py',
    )
