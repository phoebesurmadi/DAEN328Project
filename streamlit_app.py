import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Setup
st.set_page_config(page_title="Chicago Food Inspections", layout="wide")
st.title("🍽️ Chicago Food Inspections: Deep Dive Dashboard")
st.markdown("Use the filters on the left to explore inspections based on risk, location, and facility type.")

# Connect to the database
engine = create_engine(DB_URL)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM inspection_db;", con=engine)
    df['inspection_date'] = pd.to_datetime(df['inspection_date'])
    return df

df = load_data()

# Sidebar Filters
with st.sidebar:
    st.header("🔎 Filters")
    with st.expander("📍 Filter by Location"):
        zip_filter = st.multiselect("Zip Code", df["zip"].dropna().unique(), default=df["zip"].dropna().unique())
    with st.expander("⚠️ Filter by Risk Level"):
        risk_filter = st.multiselect("Risk Level", df["risk"].dropna().unique(), default=df["risk"].dropna().unique())
    with st.expander("🏢 Filter by Facility Type"):
        type_filter = st.multiselect("Facility Type", df["facility_type"].dropna().unique(), default=df["facility_type"].dropna().unique())

df = df[
    df["zip"].isin(zip_filter) &
    df["risk"].isin(risk_filter) &
    df["facility_type"].isin(type_filter)
]

# Key Metrics
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Inspections", len(df))
col2.metric("Unique Businesses", df['aka_name'].nunique())
col3.metric("Risk Levels", df['risk'].nunique())
col4.metric("Facility Types", df['facility_type'].nunique())
st.divider()

# Risk Pie Chart
risk_pie = px.pie(df, names="risk", title="Risk Level Breakdown", hole=0.4)
st.plotly_chart(risk_pie, use_container_width=True)

# Inspection Results Count
st.subheader("📋 Inspection Results Breakdown")
result_counts = df["results"].value_counts().reset_index()
result_counts.columns = ["result", "count"]
result_fig = px.bar(result_counts, x='result', y='count', color='result', title="Inspection Results Count")
st.plotly_chart(result_fig, use_container_width=True)

# Facility Type Analysis
st.subheader("🏷️ Facility Type Inspection Patterns")
top_facilities = df['facility_type'].value_counts().nlargest(10).reset_index()
top_facilities.columns = ['facility_type', 'count']
fig = px.bar(top_facilities, x='count', y='facility_type', orientation='h', color='count', color_continuous_scale='Tealgrn')
fig.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig, use_container_width=True)

# Facility Type vs Results Heatmap
st.subheader("🏪 Facility Type vs Results")
pivot = df.pivot_table(index="facility_type", columns="results", aggfunc="size", fill_value=0)
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
plt.title("Facility Type vs Results")
st.pyplot(fig)

# Risk Level Section
def visualize_risk_level(df, risk_level, risk_label):
    st.subheader(f"📌 {risk_label} Inspections Overview")
    risk_data = df[df['risk'] == risk_level]

    st.subheader("**Top 7 Facility Types**")
    top_facilities_df = risk_data['facility_type'].value_counts().nlargest(10).reset_index()
    top_facilities_df.columns = ['Facility Type', 'Count']
    bar_fig = px.bar(
        top_facilities_df,
        x='Count',
        y='Facility Type',
        orientation='h',
        title="Top 7 Facility Types",
        color='Count',
        color_continuous_scale='Tealgrn'
    )
    bar_fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(bar_fig, use_container_width=True)


    st.subheader("**Facility Type Distribution**")
    facility_counts = risk_data['facility_type'].value_counts()
    top_facilities = facility_counts.nlargest(10)
    other_count = facility_counts.sum() - top_facilities.sum()
    facility_labels = list(top_facilities.index) + ['Other']
    facility_sizes = list(top_facilities.values) + [other_count]
    # Create a Plotly donut chart
    pie_df = pd.DataFrame({
        "Facility Type": facility_labels,
        "Count": facility_sizes
    })
    pie_fig = px.pie(
        pie_df,
        names="Facility Type",
        values="Count",
        title=f"Facility Type Distribution for {risk_label}",
        hole=0.4
    )
    pie_fig.update_traces(textinfo='percent+label', hoverinfo='label+value+percent')
    st.plotly_chart(pie_fig, use_container_width=True)


    st.subheader("**Inspection Locations Map**")
    map_data = risk_data.dropna(subset=['latitude', 'longitude']).head(2000)
    if not map_data.empty:
        m = folium.Map(location=[map_data['latitude'].mean(), map_data['longitude'].mean()], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in map_data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row['aka_name']
            ).add_to(marker_cluster)
        map_height = 500 if not map_data.empty else 200
        st_folium(m, width=1000, height=map_height)

        st.markdown("<div style='margin-top:-100px;'></div>", unsafe_allow_html=True)

    else:
        st.info("No location data available for this risk level.")

visualize_risk_level(df, 'Risk 1 (High)', 'Risk 1 (High)')
visualize_risk_level(df, 'Risk 2 (Medium)', 'Risk 2 (Medium)')
visualize_risk_level(df, 'Risk 3 (Low)', 'Risk 3 (Low)')

# Map of Inspection Results
st.subheader("🗺️ Map View")
map_option = st.radio("Choose Map Type:", ["Recent Inspections", "High Risk", "Medium Risk", "Low Risk", "By Result"])

if map_option == "Recent Inspections":
    map_data = df.dropna(subset=["latitude", "longitude"]).sort_values("inspection_date", ascending=False).head(500)

elif map_option == "High Risk":
    map_data = df[df['risk'] == 'Risk 1 (High)'].dropna(subset=["latitude", "longitude"])

elif map_option == "Medium Risk":
    map_data = df[df['risk'] == 'Risk 2 (Medium)'].dropna(subset=["latitude", "longitude"])

elif map_option == "Low Risk":
    map_data = df[df['risk'] == 'Risk 3 (Low)'].dropna(subset=["latitude", "longitude"])

else:  # By Result
    result_choice = st.selectbox("Select Result Type", df['results'].dropna().unique())
    map_data = df[df['results'] == result_choice].dropna(subset=["latitude", "longitude"])

# Display interactive map
map_fig = px.scatter_mapbox(
    map_data,
    lat="latitude", lon="longitude",
    color="results",
    hover_name="aka_name",
    hover_data=["inspection_date", "facility_type", "risk"],
    zoom=10,
    height=500
)
map_fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(map_fig, use_container_width=True)

# --- Violation Cleaning & Expansion ---
df_viol = df.dropna(subset=['violations']).copy()
df_viol['violations'] = df_viol['violations'].astype(str)

# Split violations by whitespace, explode, and clean
df_viol = df_viol.assign(
    violation=df_viol['violations'].str.split()
).explode('violation')

# Keep only numeric codes, drop blanks/NaNs
df_viol = df_viol[df_viol['violation'].str.isnumeric()]
df_viol['violation'] = df_viol['violation'].astype(int)

#20 common violations
st.subheader("🚨 Top 20 Most Common Violations")
top_viol = df_viol['violation'].value_counts().nlargest(20).reset_index()
top_viol.columns = ['Violation Code', 'Count']

fig = px.bar(
    top_viol,
    x='Count',
    y='Violation Code',
    orientation='h',
    color='Count',
    color_continuous_scale='Reds',
    title="Top 20 Violation Codes Across All Inspections"
)
fig.update_layout(
    yaxis=dict(autorange='reversed'),
    plot_bgcolor='white',
    margin=dict(l=40, r=20, t=40, b=40)
)
st.plotly_chart(fig, use_container_width=True)

#violation distributions
st.subheader("🏢 Violation Distribution by Facility Type")
fac_viol = df_viol.groupby(['facility_type', 'violation']).size().reset_index(name='Count')

tree_fig = px.treemap(
    fac_viol,
    path=['facility_type', 'violation'],
    values='Count',
    title="Facility Type → Violation Code Treemap"
)
tree_fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
st.plotly_chart(tree_fig, use_container_width=True)

#sites with specific violation
st.subheader("🗺️ Map: Sites with a Specific Violation")

selected_violation = st.selectbox("Choose Violation Code", sorted(df_viol['violation'].unique()))
map_subset = df_viol[df_viol['violation'] == selected_violation].dropna(subset=['latitude', 'longitude'])

map_fig = px.scatter_mapbox(
    map_subset,
    lat="latitude",
    lon="longitude",
    color="risk",
    hover_name="aka_name",
    hover_data=["inspection_date", "facility_type", "results"],
    zoom=10,
    height=500
)
map_fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r":0, "t":30, "l":0, "b":0},
    title=f"Facilities with Violation Code {selected_violation}"
)
st.plotly_chart(map_fig, use_container_width=True)

# business w specifiv iolation
st.subheader("🏪 Businesses with Selected Violation")

selected_code = st.selectbox("Select Violation Code to View Businesses", sorted(df_viol['violation'].unique()))
viol_subset = df_viol[df_viol['violation'] == selected_code]

aka_viol = viol_subset['aka_name'].value_counts().nlargest(15).reset_index()
aka_viol.columns = ['Business Name', 'Violation Count']

biz_fig = px.bar(
    aka_viol,
    x='Violation Count',
    y='Business Name',
    orientation='h',
    color='Violation Count',
    color_continuous_scale='Teal',
    title=f"Top 15 Businesses with Violation Code {selected_code}"
)
biz_fig.update_layout(
    yaxis=dict(autorange='reversed'),
    plot_bgcolor='white',
    margin=dict(l=40, r=20, t=40, b=40)
)
st.plotly_chart(biz_fig, use_container_width=True)

# Data Table & Download
st.subheader("📄 Explore & Download Data")
st.dataframe(df, use_container_width=True)
st.download_button("📥 Download CSV", df.to_csv(index=False), "food_inspections.csv", "text/csv")

