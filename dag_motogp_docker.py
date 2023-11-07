from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.operators.bash import BashOperator

import pendulum

local_tz = pendulum.timezone("Europe/Paris")

default_args = {
    "owner": "Alex LASNIER",
    "depends_on_past": False,
    "email": ["alex.lasnier30@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    "motogp_project_docker",
    start_date=datetime(2023, 12, 1, tzinfo=local_tz),
    schedule_interval="30 8 * * 1",
    tags=[
        "motoGP",
    ],
) as dag:
    task1 = BashOperator(
        task_id="start_container",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="docker start brave_antonelli",
    )
    task2 = BashOperator(
        task_id="run_container",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="docker exec brave_antonelli python scraper.py > output_scraper.txt",
    )
    task3 = BashOperator(
        task_id="stop_container",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="docker stop brave_antonelli",
    )

    task1 >> task2 >> task3
