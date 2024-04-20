# Real-time Election Voting System
===============================
## Table of Contents
- [Introduction](#introduction)
- [Project Architecture](#project-architecture)
- [System Components](#system-components)
- [Screen shots](#screen-shots)

## Introduction
This repository contains the code for a realtime election voting system. The system is built using Python, Kafka, Spark Streaming, Postgres and Streamlit. The system is built using Docker Compose to easily spin up the required services in Docker containers.

## Project Architecture
![system_architecture.png](images/system_architecture.png)

Essential components for this project are:
- **Data Source**: [randomuser.me](https://randomuser.me/) API as the starting point of the project to generate random user data.
- **Apache Kafka and Zookeeper**: Used for streaming data from PostgreSQL to the processing engine.
- **Apache Spark**: Data processor unit of the system. Contains one master&worker.
- **Postgres**: Where the data will be stored.

## System Components
- **main.py**: This is the main Python script that creates the required tables on postgres (`candidates`, `voters` and `votes`), it also creates the Kafka topic and creates a copy of the `votes` table in the Kafka topic. It also contains the logic to consume the votes from the Kafka topic and produce data to `voters_topic` on Kafka.
```bash
python main.py
```
- **voting.py**: This is the Python script that contains the logic to consume the votes from the Kafka topic (`voters_topic`), generate voting data and produce data to `votes_topic` on Kafka.
```bash
python voting.py
```
- **spark-streaming.py**: This is the Python script that contains the logic to consume the votes from the Kafka topic (`votes_topic`), enrich the data from postgres and aggregate the votes and produce data to specific topics on Kafka.
```bash
python spark-streaming.py
```
- **streamlit-app.py**: This is the Python script that contains the logic to consume the aggregated voting data from the Kafka topic as well as postgres and display the voting data in realtime using Streamlit.
```bash
streamlit run streamlit-app.py
```

## Screen shots
### Dashboard

