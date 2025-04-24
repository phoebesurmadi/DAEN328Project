import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DB_URL")

# Setup
st.set_page_config(page_title="Chicago Food Inspections", layout="wide")
st.title("🍽️ Chicago Food Inspections: Deep Dive Dashboard")

# Connect to DB
engine = create_engine(DB_URL)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM inspection_db;", con=engine)
    df['inspection_date'] = pd.to_datetime(df['inspection_date'])
    return df
df = load_data()

# Filters
#st.sidebar.header("🔎 Filters")
#zip_filter = st.sidebar.multiselect("Zip Code", df["zip"].dropna().unique(), default=df["zip"].dropna().unique())
#risk_filter = st.sidebar.multiselect("Risk Level", df["risk"].dropna().unique(), default=df["risk"].dropna().unique())
#type_filter = st.sidebar.multiselect("Facility Type", df["facility_type"].dropna().unique(), default=df["facility_type"].dropna().unique())

#df = df[
#    df["zip"].isin(zip_filter) &
#    df["risk"].isin(risk_filter) &
#    df["facility_type"].isin(type_filter)
#]

# KPIs
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Inspections", len(df))
col2.metric("Unique Businesses", df['dba_name'].nunique())
col3.metric("Risk Levels", df['risk'].nunique())
col4.metric("Facility Types", df['facility_type'].nunique())
st.divider()

# Risk Distribution
# st.subheader("🧯 Risk Category Distribution")
# risk_fig = px.histogram(df, x="risk", color="risk", title="Distribution by Risk Level")
# st.plotly_chart(risk_fig, use_container_width=True)

# Pie Chart
risk_pie = px.pie(df, names="risk", title="Risk Level Breakdown", hole=0.4)
st.plotly_chart(risk_pie, use_container_width=True)

# Inspection Results Breakdown
st.subheader("📋 Inspection Results Breakdown")

# Count the number of each inspection result and rename columns
result_counts = df["results"].value_counts().reset_index()
result_counts.columns = ["result", "count"]

# Create bar chart
result_fig = px.bar(
    result_counts,
    x='result',
    y='count',
    color='result',
    title="Inspection Results Count"
)

st.plotly_chart(result_fig, use_container_width=True)

# Facility Type vs Results Heatmap
st.subheader("🏪 Facility Type vs Results")
pivot = df.pivot_table(index="facility_type", columns="results", aggfunc="size", fill_value=0)
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
plt.title("Facility Type vs Results")
st.pyplot(fig)

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Define a function to create visualizations for each risk level
def visualize_risk_level(df, risk_level, risk_label):
    st.subheader(f"📌 {risk_label} Inspections Overview")

    # Filter data for the specified risk level
    risk_data = df[df['risk'] == risk_level]

    # Bar Chart: Top 10 Facility Types
    st.subheader("**Top 10 Facility Types**")
    top_facilities = risk_data['facility_type'].value_counts().nlargest(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_facilities.values, y=top_facilities.index, ax=ax)
    ax.set_xlabel("Number of Inspections")
    ax.set_ylabel("Facility Type")
    st.pyplot(fig)

    # Pie Chart: Facility Type Distribution
    st.subheader("**Facility Type Distribution**")
    facility_counts = risk_data['facility_type'].value_counts()
    top_facilities = facility_counts.nlargest(10)
    other_count = facility_counts.sum() - top_facilities.sum()
    facility_labels = list(top_facilities.index) + ['Other']
    facility_sizes = list(top_facilities.values) + [other_count]
    fig, ax = plt.subplots()
    ax.pie(facility_sizes, labels=facility_labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

    # Map: Inspection Locations
    st.subheader("**Inspection Locations Map**")
    map_data = risk_data.dropna(subset=['latitude', 'longitude']).head(2000)
    if not map_data.empty:
        m = folium.Map(location=[map_data['latitude'].mean(), map_data['longitude'].mean()], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        for idx, row in map_data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row['dba_name']
            ).add_to(marker_cluster)
        st_folium(m, width=700, height=500)
    else:
        st.info("No location data available for this risk level.")

# Call the function for each risk level
visualize_risk_level(df, 'Risk 1 (High)', 'Risk 1 (High)')
visualize_risk_level(df, 'Risk 2 (Medium)', 'Risk 2 (Medium)')
visualize_risk_level(df, 'Risk 3 (Low)', 'Risk 3 (Low)')

#2.3 visualization for facility type
st.subheader("Visualization for Facility Type")

fig, ax = plt.subplots(2, 2, figsize=(20, 16))

# Top 10 Facility Types by Inspection Count
top_facilities = df['facility_type'].value_counts().nlargest(10)
sns.barplot(x=top_facilities.values, y=top_facilities.index, ax=ax[0, 0])
ax[0, 0].set_title("Top 10 Facility Types by Inspection Count", fontsize=20)
ax[0, 0].set_xlabel('Counts', fontsize=18)
ax[0, 0].set_ylabel('')

# Distribution of Inspections for Restaurants
restaurant_data = df[df['facility_type'] == 'Restaurant']
sns.scatterplot(x='longitude', y='latitude', hue='risk', data=restaurant_data, ax=ax[0, 1])
ax[0, 1].set_title("Distribution of Inspections for Restaurants", fontsize=20)
ax[0, 1].set_xlabel('Longitude')
ax[0, 1].set_ylabel('Latitude')

# Distribution of Inspections for Grocery Stores
grocery_data = df[df['facility_type'] == 'Grocery Store']
sns.scatterplot(x='longitude', y='latitude', hue='risk', data=grocery_data, ax=ax[1, 0])
ax[1, 0].set_title("Distribution of Inspections for Grocery Stores", fontsize=20)
ax[1, 0].set_xlabel('Longitude')
ax[1, 0].set_ylabel('Latitude')

# Distribution of Inspections for Schools
school_data = df[df['facility_type'] == 'School']
sns.scatterplot(x='longitude', y='latitude', hue='risk', data=school_data, ax=ax[1, 1])
ax[1, 1].set_title("Distribution of Inspections for Schools", fontsize=20)
ax[1, 1].set_xlabel('Longitude')
ax[1, 1].set_ylabel('Latitude')

st.pyplot(fig)

#2.4 visualization
st.subheader("Visualization for Results of Inspection")
fig, ax = plt.subplots(2, 2, figsize=(20, 16))

# Counts of Inspection Results
result_counts = df['results'].value_counts()
sns.barplot(x=result_counts.index, y=result_counts.values, ax=ax[0, 0])
ax[0, 0].set_title("Counts of Inspection Results", fontsize=20)
ax[0, 0].set_ylabel('Counts', fontsize=18)
ax[0, 0].set_xlabel('')

# Counts of Inspection Results by Year
df['year'] = df['inspection_date'].dt.year
results_by_year = df.groupby(['results', 'year']).size().unstack('results')
results_by_year.plot(kind='bar', ax=ax[0, 1])
ax[0, 1].set_title("Counts of Inspection Results by Year", fontsize=20)
ax[0, 1].set_ylabel('Counts', fontsize=18)
ax[0, 1].legend(title='Results', bbox_to_anchor=(1.05, 1), loc='upper left')

# Distribution of Passed Inspections
pass_data = df[df['results'] == 'Pass']
sns.scatterplot(x='longitude', y='latitude', hue='risk', data=pass_data, ax=ax[1, 0])
ax[1, 0].set_title("Distribution of Passed Inspections", fontsize=20)
ax[1, 0].set_xlabel('Longitude')
ax[1, 0].set_ylabel('Latitude')

# Distribution of Failed Inspections
fail_data = df[df['results'] == 'Fail']
sns.scatterplot(x='longitude', y='latitude', hue='risk', data=fail_data, ax=ax[1, 1])
ax[1, 1].set_title("Distribution of Failed Inspections", fontsize=20)
ax[1, 1].set_xlabel('Longitude')
ax[1, 1].set_ylabel('Latitude')

st.pyplot(fig)

# Map of Recent Inspections
st.subheader("🗺️ Recent Inspection Locations")
recent_df = df.dropna(subset=["latitude", "longitude"]).sort_values("inspection_date", ascending=False).head(500)
map_fig = px.scatter_mapbox(
    recent_df,
    lat="latitude", lon="longitude",
    color="results",
    hover_name="dba_name",
    hover_data=["inspection_date", "facility_type", "risk"],
    zoom=10,
    height=500
)
map_fig.update_layout(mapbox_style="carto-positron")
st.plotly_chart(map_fig, use_container_width=True)

# Data Table
st.subheader("📄 Explore Cleaned Data")
st.dataframe(df)
