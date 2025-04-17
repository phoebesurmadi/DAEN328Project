import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv(dotenv_path=".env.sample")
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

# Violation Keyword Frequency
st.subheader("🚨 Most Common Violations (Keywords)")
if 'violation_description' in df.columns:
    violations = df['violation_description'].dropna().str.lower().str.split('. ')
    keywords = pd.Series([item for sublist in violations for item in sublist])
    top_violations = keywords.value_counts().head(10)
    fig, ax = plt.subplots()
    top_violations.plot(kind='barh', ax=ax)
    ax.set_title("Top 10 Violation Phrases")
    ax.invert_yaxis()
    st.pyplot(fig)

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

# Interactive Business Timeline
st.subheader("🏢 Business Inspection History (Interactive)")
biz_list = sorted(df['dba_name'].unique())
selected_biz = st.selectbox("Select Business", biz_list)
biz_df = df[df['dba_name'] == selected_biz].sort_values("inspection_date")

if not biz_df.empty:
    timeline = px.timeline(
        biz_df,
        x_start="inspection_date", x_end="inspection_date",
        y="inspection_type", color="results",
        hover_data=["risk", "facility_type", "zip"],
        title=f"Inspection Timeline for {selected_biz}"
    )
    timeline.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(timeline, use_container_width=True)
else:
    st.info("No inspections available for this business.")

# Data Table
st.subheader("📄 Explore Cleaned Data")
st.dataframe(df)
