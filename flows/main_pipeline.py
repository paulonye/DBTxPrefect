"""This Data Pipeline collects data from Google Cloud Storage Bucket, and \
    loads it into a Bigquery Warehoiuse"""

from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket


@task(retries=3, tags=["extract"])
def extract_from_gcs(table) -> Path:
    """Download table from GCS"""
    gcs_path = f"data/{table}"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path="./load")
    path = Path(f"./load/data/{table}")
    return path


@task(log_prints=True, tags=['Tranform Schema to Bigquery Standard'])
def convert_to_bigquery_types(path: Path) -> pd.DataFrame:
    """Convert the Data Type to a Standard Scheme"""

    df = pd.read_csv(path)

    for col in df.columns:
        # check the data type of the column
        dtype = df[col].dtype

        print(dtype)
        
        # convert to BigQuery-compatible types
        if dtype == 'object':
            df[col] = df[col].astype('str')
        elif dtype == 'bool':
            df[col] = df[col].astype('str')
        elif dtype == 'int':
            df[col] = df[col].astype('int')
        elif dtype == 'float':
            df[col] = df[col].astype('float')
        elif dtype == 'datetime':
            df[col] = df[col].astype('datetime')
     
    return df



@task(tags=["load to bq"])
def load_bigquery(df: pd.DataFrame, table_name: str) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("zoom")

    table_name = table_name.strip('.csv')

    #Ensure you create the Schema on Bigquery
    df.to_gbq(
        destination_table=f"mixmax_staging.{table_name}",
        project_id="sendme-test-db",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="replace",
    )

@flow()
def load_data_to_bigquery(table: str):
    df_table = extract_from_gcs(table)
    df_table = convert_to_bigquery_types(df_table)
    load_bigquery(df_table, table)

@flow()
def load_all_to_bigquery(tables: list[str] = ['table1', 'table2']):
    for table in tables:
        load_data_to_bigquery(table)

if __name__ == '__main__':
    tables = ['dim_features.csv', 'plan_feature_definitions.csv', 'prepaid_account.csv',
                'stripe_arr.csv', 'users.csv', 'workspaces.csv', 'workspaces_feature_usage_weekly.csv']

    load_all_to_bigquery(tables)
