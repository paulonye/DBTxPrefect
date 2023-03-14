from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp import GcpCredentials
from prefect_sqlalchemy import SqlAlchemyConnector


@task(log_prints=True, tags=['Extract from Postgres'])
def extract_from_postgres(table_name: str) -> pd.DataFrame:

    """This function extracts the data from a postgres database
            function args:
                - TABLE: The name of the table to extract data from
                
            Output:
                - Dataframe Object: The filepath of the saved file is returned"""


    connection_block = SqlAlchemyConnector.load("postgres-connector")


    with connection_block.get_connection(begin=False) as engine:

        query = f"""select * from {table_name}"""

        print(query)

        df_table = pd.read_sql(query, engine)

        df_table = df_table.drop(['index'], axis =1)

        print('Load Successful')

        engine.connect().close()

        return df_table


@task(log_prints=True, tags=['Tranform Schema to Bigquery Standard'])
def convert_to_bigquery_types(df: pd.DataFrame) -> pd.DataFrame:
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
        elif dtype == 'datetime64[ns]':
            df[col] = df[col].astype('datetime')
     
    return df



@task(tags=["load to bq"])
def load_bigquery(df: pd.DataFrame, table_name: str) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("zoom")

    df.to_gbq(
        destination_table=f"mixmax_staging.{table_name}",
        project_id="sendme-test-db",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="replace",
    )

@flow()
def load_data_to_bigquery(table):
    df_table = extract_from_postgres(table)
    df_table = convert_to_bigquery_types(df_table)
    load_bigquery(df_table, table)

@flow()
def load_all_to_bigquery(tables: list[str] = ['table1', 'table2']):
    for table in tables:
        load_data_to_bigquery(table)

if __name__ == '__main__':
    tables = ['dim_features_table', 'plan_feature_definitions_table', 'prepaid_account_table', 'stripe_arr_table',
               'users_table', 'workspaces_feature_usage_weekly_table',  'workspaces_table']

    load_all_to_bigquery(tables)
