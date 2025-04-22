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
st.sidebar.header("🔎 Filters")
zip_filter = st.sidebar.multiselect("Zip Code", df["zip"].dropna().unique(), default=df["zip"].dropna().unique())
risk_filter = st.sidebar.multiselect("Risk Level", df["risk"].dropna().unique(), default=df["risk"].dropna().unique())
type_filter = st.sidebar.multiselect("Facility Type", df["facility_type"].dropna().unique(), default=df["facility_type"].dropna().unique())

df = df[
    df["zip"].isin(zip_filter) &
    df["risk"].isin(risk_filter) &
    df["facility_type"].isin(type_filter)
]

# KPIs
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Inspections", len(df))
col2.metric("Unique Businesses", df['dba_name'].nunique())
col3.metric("Risk Levels", df['risk'].nunique())
col4.metric("Facility Types", df['facility_type'].nunique())

st.divider()

# Risk Distribution
st.subheader("🧯 Risk Category Distribution")
risk_fig = px.histogram(df, x="risk", color="risk", title="Distribution by Risk Level")
st.plotly_chart(risk_fig, use_container_width=True)

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

# Monthly Trend
st.subheader("📅 Monthly Trend of Inspections")
monthly = df.groupby(df['inspection_date'].dt.to_period("M")).size().reset_index(name='count')
monthly["inspection_date"] = monthly["inspection_date"].dt.to_timestamp()
trend_fig = px.line(monthly, x="inspection_date", y="count", title="Monthly Number of Inspections")
st.plotly_chart(trend_fig, use_container_width=True)

# Facility Type vs Results Heatmap
st.subheader("🏪 Facility Type vs Results")
pivot = df.pivot_table(index="facility_type", columns="results", aggfunc="size", fill_value=0)
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
plt.title("Facility Type vs Results")
st.pyplot(fig)

# Zip vs Results
st.subheader("📍 ZIP Code vs Results Heatmap")
pivot2 = df.pivot_table(index="zip", columns="results", aggfunc="size", fill_value=0)
fig2, ax2 = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot2, annot=True, fmt="d", cmap="Greens", ax=ax2)
plt.title("Zip Code vs Result Count")
st.pyplot(fig2)

# 2.3 Visualization for Facility Type
st.subheader("🏬 Facility Type Analysis")

fig, ax = plt.subplots(2, 2, figsize=(20, 16))

# Top 10 facility types
top_facilities = df['facility_type'].value_counts().head(10)
sns.barplot(x=top_facilities.values, y=top_facilities.index, ax=ax[0, 0])
ax[0, 0].set_title("Top 10 Facility Types by Count of Inspections", size=20)
ax[0, 0].set_xlabel("Counts", size=18)
ax[0, 0].set_ylabel("")

# Restaurant scatterplot
sns.scatterplot(
    lat="latitude", lon="longitude",
    hue="risk", data=df[df['facility_type'] == 'restaurant'],
    ax=ax[0, 1]
)
ax[0, 1].set_title("Inspections for Restaurants", size=20)
ax[0, 1].set_xlabel("Longitude")
ax[0, 1].set_ylabel("Latitude")

# Grocery Store scatterplot
sns.scatterplot(
    lat="latitude", lon="longitude",
    hue="risk", data=df[df['facility_type'] == 'grocery store'],
    ax=ax[1, 0]
)
ax[1, 0].set_title("Inspections for Grocery Stores", size=20)
ax[1, 0].set_xlabel("Longitude")
ax[1, 0].set_ylabel("Latitude")

# School scatterplot
sns.scatterplot(
    lat="latitude", lon="longitude",
    hue="risk", data=df[df['facility_type'] == 'school'],
    ax=ax[1, 1]
)
ax[1, 1].set_title("Inspections for Schools", size=20)
ax[1, 1].set_xlabel("Longitude")
ax[1, 1].set_ylabel("Latitude")

st.pyplot(fig)

# 2.4 Visualization for Results of Inspection
st.subheader("📑 Inspection Result Trends")

fig, ax = plt.subplots(2, 2, figsize=(20, 16))

# Bar chart for overall result counts
result_counts = df["results"].value_counts()
sns.barplot(x=result_counts.index, y=result_counts.values, ax=ax[0, 0])
ax[0, 0].set_title("Counts of Inspection Results", size=20)
ax[0, 0].set_ylabel("Counts", size=18)
ax[0, 0].set_xlabel("")

# Add 'year' column for time-based grouping
df["year"] = df["inspection_date"].dt.year

# Group by results and year
results_by_year = df.groupby(["results", "year"])["inspection_id"].count().unstack("results")
results_by_year.plot(kind="bar", ax=ax[0, 1])
ax[0, 1].tick_params(axis="x", labelrotation=360)
ax[0, 1].legend(loc="upper left", fontsize=14, bbox_to_anchor=(1.15, 0.75))
ax[0, 1].set_title("Counts of Inspection Results by Year", size=20)
ax[0, 1].set_ylabel("Counts", size=18)

# Scatter for "Pass"
sns.scatterplot(
    lat="latitude", lon="longitude",
    hue="risk", data=df[df["results"] == "pass"],
    ax=ax[1, 0]
)
ax[1, 0].set_title("Geographic Distribution of Passed Inspections", size=20)
ax[1, 0].set_xlabel("Longitude")
ax[1, 0].set_ylabel("Latitude")

# Scatter for "Fail"
sns.scatterplot(
    lat="latitude", lon="longitude",
    hue="risk", data=df[df["results"] == "fail"],
    ax=ax[1, 1]
)
ax[1, 1].set_title("Geographic Distribution of Failed Inspections", size=20)
ax[1, 1].set_xlabel("Longitude")
ax[1, 1].set_ylabel("Latitude")

st.pyplot(fig)

# Time between inspections
st.subheader("⏱️ Time Between Inspections")
biz_time = df.sort_values(["dba_name", "inspection_date"]).copy()
biz_time["prev_date"] = biz_time.groupby("dba_name")["inspection_date"].shift()
biz_time["days_between"] = (biz_time["inspection_date"] - biz_time["prev_date"]).dt.days

fig3, ax3 = plt.subplots()
sns.boxplot(data=biz_time.dropna(subset=["days_between"]), x="risk", y="days_between", ax=ax3)
plt.title("Days Between Inspections by Risk Level")
st.pyplot(fig3)

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
