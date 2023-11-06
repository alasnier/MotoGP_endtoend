from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator

import pendulum

local_tz = pendulum.timezone("Europe/Paris")

default_args = {
    "owner": "Alex LASNIER,
    "depends_on_past": False,
    "email": ["alex.lasnier30@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    "motogp_project",
    start_date=datetime(2023, 12, 01, tzinfo=local_tz),
    schedule_interval="30 8 * * 1",
    tags=[
        "motoGP",
    ],
) as dag:
    task1 = BashOperator(
        task_id="SearchDbSync.dll",
        retries=4,
        retry_delay=timedelta(minutes=20),
        default_args=default_args,
        bash_command="cd /data/DATALAB/coyote/prg/dotnetprg/SearchDb/SearchDb/bin/Release/net6.0 && /opt/dotnet6/dotnet exec SearchDb.dll",
    )
    task2 = BashOperator(
        task_id="DailyReportUsage.dll",
        default_args=default_args,
        bash_command="cd /data/DATALAB/coyote/prg/dotnetprg/MonthStat/DailyReportUsage/bin/Release && /opt/dotnet6/dotnet exec net6.0/DailyReportUsage.dll",
    )

    task3 = SSHOperator(
        task_id="requirements",
        default_args=default_args,
        ssh_hook=sshHook,
        command="docker exec python_container pip install -r /data/DATALAB/coyote/prg/pythonprg/data/alerting_fcd/requirements.txt",
    )

    task4 = SSHOperator(
        task_id="session_parquet",
        default_args=default_args,
        ssh_hook=sshHook,
        command="docker exec python_container bash -c 'export AIRFLOW_CTX_EXECUTION_DATE={{ds}} && python /data/DATALAB/coyote/prg/pythonprg/data/alerting_fcd/txt_to_parquet-byday_final.py'",
    )

    task1 >> [task2, task3]
    task3 >> task4
