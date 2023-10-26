from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

import pendulum

local_tz = pendulum.timezone("Europe/Paris")

default_args = {
    "owner": "data",
    "depends_on_past": False,
    "email": ["datalab@coyote-group.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

sshHook = SSHHook(ssh_conn_id="zvp-ldtl001")


with DAG(
    "sync_customers",
    start_date=datetime(2021, 11, 18, tzinfo=local_tz),
    schedule_interval="30 6 * * *",
    tags=[
        "Fcd",
        "Elasticsearch",
        "Customers",
        "Daily",
        "Report",
        "PowerBI",
        "Belgium",
        "P&S",
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
