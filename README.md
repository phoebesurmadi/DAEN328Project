# Team 1: Final Project

Project Overview:

In this project we build a complete, modular, and dockerized ETL pipeline of data from the Chicago Food Inspections API. The final project...

1. Fetches data from the API
2. Cleans the data
3. Stores the clean data in PostgreSQL
4. Visualizes it using Streamlit
5. Is fully dockerized using Docker and Docker Compose

Data Descriptions:
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


Instructions:


Contributions:
Madeline - Extraction, Cleaning, Dockerizing

...
