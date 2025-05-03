
FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
#CMD python extract.py && python transform.py && python load.py && streamlit run streamlit_app.py

