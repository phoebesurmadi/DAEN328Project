# Team 1: Final Project

# Overview

## **Project Overview**
In this project we build a complete, modular, and dockerized ETL pipeline of data from the Chicago Food Inspections API. The API holds information on individual inspection records in Chicago, IL, updated in real time. The final project...

1. Fetches data from the API
2. Cleans the data
3. Stores the clean data in PostgreSQL
4. Visualizes it using Streamlit
5. Is fully dockerized using Docker and Docker Compose


## **Data Descriptions**

'inspection_id': unique inspection ID

'aka_name': name of establishment

'license_': unique business ID

'facility_type': restaurant, grocery store, etc.

'risk': 1 of 3 risk types (high, low, medium) 

'address': street address 

'zip': zip code

'violations': string list of violations

'inspection_date' in datetime (2025-04-07 for example)

'inspection_type': one of many inspection types

'results': out of business, pass, etc

'latitude', 'longitude': float values

# Instructions
First, cd the copied repository folder and source your activate file if using a venv:
- cd <repo/path>
- source <activate/path>

Then, after opening postgres, copy the .env.sample file and replace the password with your postgres password.
- run: cp .env.sample .env
  
The entire Docker system can be run using
- docker-compose up --build

If you want to clean up old images and run things a bit more separated, run the following in command prompt or terminal to shut down any previously run images and delete any old images to start from scratch:
- docker-compose down --volumes --remove-orphans
- docker rmi $(docker images -q) -f

Then to build and run the app:
- docker-compose build --no-cache
- docker-compose up
 
(Extracting and loading into the database may take a while, but eventually terminal/command prompt will display the link to Streamlit. Don't open the streamlit link in your browser until terminal/command prompt displays '✅ Data loading complete.')

- Streamlit Link: http://0.0.0.0:8501 or http://localhost:8501
# Postgres Setup
![Image](images/Postgres_Setup.png?raw=true)

# Streamlit 
The top of the streamlit page. Title and some basic data info.
![Image](images/streamlit1.png?raw=true)

Example of using the interactive side panel and an interactive map view of 'results' by location.
![Image](images/streamlit2.png?raw=true)

# Contributions

Madeline - Extraction, Cleaning, Dockerizing

Phoebe - Streamlit App, Visualizations, Dockerizing

Luis - Load.py, Database Structuring, Dockerizing


