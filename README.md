# MIXMAX DATA PIPELINE

>In this project, Prefect is used to orchestrate an Extract Load Transform Pipeline application alongside all its dependencies.
>
>The Pipeline will be deployed on a serverless platform using Google Cloud Run
>
>The goal of the pipeline is to:
> - Collect data from a postgres database 
> - Load the data into a Staging schema of the Bigquery data warehouse
> - Perform transformations and write data tests using DBT
> - Load the transformed tables into a Production/Analytics schema in the data warehouse
> - Report the Metrics on a Dashboard
> - Set up Prefect Automations to monitor Pipeline

## Project Structure
- Prerequisites
- Setting up the Environment
- Building the Loading Pipeline into Postgres
- Building the Main Pipeline into Bigquery
- Building the Models using DBT
- Building the Docker Image for Deployment
- Deploying the Pipeline on Prefect Cloud
- Scheduling the Deployment 
- Reporting with Google Data Studio
- Build Prefect Automation for Error Handling

## DATA STACK

![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/mixmax_cover.png)

**INFRASTRUCTURE**
- Google Cloud Run
- Docker

**AUTHENTICATION**
- Google Cloud SDK & Service Accounts

**ORCHESTRATION & MONITORING**
- Prefect

**TRANSFORMATION**
- Data Build Tool (DBT)

**RELATIONAL DATABASE**
- Postgres

**DATABASE SQL CLIENT**
- PGADMIN

**DATA WAREHOUSE**
- Bigquery

**VISUALIZATION**
- Looker Studio

**Link to Dashboard**: https://lookerstudio.google.com/u/0/reporting/9fd8c6d4-ad33-49e6-9e85-d916e9b4e949/page/C4hBB/edit

## Prerequisite
- Set up a GCP Instance to run the deployment and host the prefect agent to pick up wokqueues. 
- Configure SSH access for remote access to the virtual machine for development.
- Set up Google Cloud sdk
- Set up the Bigquery Schema and configure a service account key for authentication. 
- Set up DBT Cloud for Transformation and Building of Data Models; and connect to the Bigquery Data Warehouse.
- Set up Prefect Cloud, and configure your virtual machine for development.
- Set up Google Data Studio and connect to Bigquery data warehouse.


## Set up your environment
Install Google Cloud SDK and authenticate using the service account key
```bash
   gcloud auth activate-service-account --key-file credentials.json
```

Set up Virtual Environment 
```bash
   python -m venv env

   source env/bin/activate
```
Install the Required Libraries in the Virtual Environment
```bash
   pip install -r requirements.txt
```
Authenticate into your Prefect Cloud Workspace on the terminal
```bash
   prefect cloud login
```
Create a docker-compose file to start up your postgres and pgadmin containers
```bash
    docker-compose up -d

    #use the command below to confirm that your containers are running
    docker ps
```
Note: Ensure you configure the containers correctly
## Building the Loading Pipeline
The Loading pipeline is used to load the csv files from a Cloud Storage Bucket into a postgres database running on a docker container. It has a subflow and a parent flow. It also contains two tasks, and two block.
Task:
- Extract the csv file from the Cloud Storage Bucket
- Load the csv file into the Postgres Database as a table
Block:
- It contains the prefect sqlalchemy block which stores your database credentails as secrets and allows you connect to your securely database.
- It contains the GCS block which is used to authenticate your Google Cloud Storageccwith your pipeline.
Others:
Parameterization was applied so that all csv files can be loaded separately
Run the pipeline to check that it works.
`python flows/load.py`
Here are the loaded tables
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/pgadmin.png)

## Building the Main Pipeline
The Main pipeline is used to extract table data from the postgres database and load it into the bigquery data warehouse. It has a subflow and a parent flow. It also contains two tasks, and one block.
Task:
- Collect table data from the postgres database
- Load the data into bigquery.
Block:
- It contains the prefect sqlalchemy block which stores your database credentails as secrets and allows you connect to your securely database.
Others:
Parameterization was applied so that the table needed can be loaded separately into Bigquery.
Run the pipeline to check that it works.
`python flows/main_pipeline.py`

## Loading the Data into Bigquery
The tables are loaded into a staging schema in Bigquery. This staging schema will be connected to the DBT models that will be used for development.
A production/analytics schema will also be created that will host the transformed tables.

## Building the Models using DBT
DBT is used to develop the models and also run tests.

### RUNNING TESTS
IN DBT, we will test the primary id of each dataset for null value and uniqueness, below is the result of the test
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/dbt_test.png)

### BUILDING THE DATA MODEL
We will use DBT to create the ff tables from the staging schema tables.
The models can be found in `dbt_models/models/core`
Here are the Models Created:

- Feature Facts Table
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/feature_facts.png)

- Users Facts Table
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/users_fact.png)

- Workspaces Facts Table
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/workspaces_fact.png)

After testing, the models are loaded as tables into the analytics schema in Bigquery.

## Build and Deploy Docker Image to Google Artifact Registry
In the directory of the cloned repo, open the `Dockerfile` and make the changes you need to make. It is well documented, so just follow through.

Authenticate to the Region where your Artifact Registry is located
```bash
   gcloud auth configure-docker us-east1-docker.pkg.dev
```
Build the Docker Image for Artifact Registry
```bash
   docker build -t us-east1-docker.pkg.dev/my-project/my-repo/mxm_pipeline:tag1 .
```
Where `my-project` is my GCP Project ID and `my-repo` is the name of my repo I created on artifact registry.
Push the Docker Image to Artifact Registry
```bash
   docker push us-east1-docker.pkg.dev/my-project/my-repo/mxm_pipeline:tag1
```

## Deploying the Flow
 To deploy the flow, the docker block is created on the prefect cloud workspace.
 Run the command to deploy
```bash
   $ prefect deployment build main_pipeline.py:load_all_to_bigquery -n test-dev -ib cloud-run-job/dev -q dev -o deployment.yaml
```
Once the deployment has been made, all the necessary parameters are added to the deployment workspace on prefect cloud.

## Running the Deployment
To run the deployment, we need to set the prefect agent in our environment
For this, we need to set it up as a detached environment, and we can do this using `tmux`
```bash
    tmux
    #this opens a new terminal window

    source emv/bin/activate
    #activate the virtual environment where you installed prefect

    prefect agent start -q "default"
    #deploy the prefect agent to pickup workqueues using the default tag

    ctrl+D, B
    #detach from the tmux window

    tmux ls
    #list the tmux sessions currently running

    tmux attach -t 0
    #reattach to the tmux session

    tmux kill-session -t 0
    #kill the session
```

## Scheduling the Deployment and the Transformation
The deployment is then scheduled on the prefect cloud workspace:

The Pipeline will run the job by 8.00 am every morning
```bash
    0 8 * * *
```
The Transformation is Scheduled on DBT Cloud in a production environment to run by 8.05 am every morning
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/transdbt.png)

## Reporting with Google Data Studio
The Bigquery tables from the Analytics schema is connected to Google Data Studio.

Here is the final dashboard:
The main dashboard which gives a snapshot of operations
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/dash1.png)
A dashboard that shows how workspaces uses mixmax features
![Cover_Image](https://nwosupaulonye.s3.amazonaws.com/dash2.png)


## Build Prefect Automation for Error Handling
A Slack webhook URL is set and connected to the prefect deployment flow, this will alert us in a slack channel if the pipeline fails.