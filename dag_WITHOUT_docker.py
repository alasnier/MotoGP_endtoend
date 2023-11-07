from __future__ import annotations


from datetime import datetime
from datetime import timedelta

import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

local_tz = pendulum.timezone("Europe/Paris")

default_args = {
    "owner": "Alex LASNIER",
    "depends_on_past": False,
    "email": ["alex.lasnier30@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    dag_id="motogp_project",
    start_date=datetime(2023, 10, 1, tzinfo=local_tz),
    schedule_interval="12 10 * * *",
    tags=[
        "motoGP",
    ],
) as dag:
    task1 = BashOperator(
        task_id="active_venv",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="source /home/alasnier/motogp_env/bin/activate > /home/alasnier/Documents/motogp/outputs/output_venv.txt",
    )
    task2 = BashOperator(
        task_id="update_upgrade",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="echo admin | sudo -S apt update -y && sudo -S apt upgrade -y > /home/alasnier/Documents/motogp/outputs/output_upgrade.txt",
    )
    task3 = BashOperator(
        task_id="Install_requirements",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="pip install -r /home/alasnier/Documents/motogp/requirements.txt > /home/alasnier/Documents/motogp/outputs/output_reqs.txt",
    )
    task4 = BashOperator(
        task_id="Run_collect_of_datas",
        retries=3,
        retry_delay=timedelta(minutes=1),
        default_args=default_args,
        bash_command="python3 /home/alasnier/Documents/motogp/scraper.py > /home/alasnier/Documents/motogp/outputs/output_scraper.txt",
    )

    task1 >> task2 >> task3 >> task4
