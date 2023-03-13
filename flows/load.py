from pathlib import Path
import pandas as pd
import datetime
from datetime import timedelta
from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect_gcp.cloud_storage import GcsBucket

##########################################################################

@task(retries=3, tags=["extract"])
def extract_from_gcs(dataset) -> Path:
    """Download dataset from GCS"""
    gcs_path = f"data/{dataset}"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"./load")
    path = Path(f"./load/data/{dataset}")
    return path


@task(log_prints=True, tags=['Load'])
def batch(path: Path, dataset: str) -> None:
    
    connection_block = SqlAlchemyConnector.load("postgres-connector")
    with connection_block.get_connection(begin=False) as engine:

        df_set = pd.read_csv(path)

        table_name = dataset.replace('.csv', '_table')

        df_set.to_sql(name=table_name, con=engine, if_exists='replace')

        print('Batch Successful')

        engine.connect().close()

@flow()
def etl_load_to_postgres(dataset):
    """Main ETL flow to load data into Snowflakes"""

    path = extract_from_gcs(dataset)
    batch(path, dataset)

@flow()
def load_mixmax_flow(
            datasets: list[str] = ['dataset1','dataset2'], 
    ):
    """Main flow for Running Pipeline"""

    for dataset in datasets:
        etl_load_to_postgres(dataset)

if __name__ == '__main__':
    datasets = ['dim_features.csv', 'plan_feature_definitions.csv', 'prepaid_account.csv',
                'stripe_arr.csv', 'users.csv', 'workspaces.csv', 'workspaces_feature_usage_weekly.csv']
    load_mixmax_flow(datasets)