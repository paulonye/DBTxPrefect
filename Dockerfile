FROM python:3.9

RUN apt-get update

COPY main_pipeline.py /opt/prefect/flows/main_pipeline.py

RUN mkdir /opt/prefect/data/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /opt/prefect/flows/