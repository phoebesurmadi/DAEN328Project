# streamlit_app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import plotly.express as px

# Load environment variables
load_dotenv()

# Database credentials
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "trends_db")

# Connect to PostgreSQL
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM trends;", engine)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")

df = load_data()

# App title
st.title("📊 Future Google Trends Explorer")

# Available columns (keywords)
available_keywords = df.columns.tolist()

# Keyword selection (user types one at a time)
st.subheader("🔤 Enter Keywords (One at a Time)")
if "selected_keywords" not in st.session_state:
    st.session_state.selected_keywords = []

new_word = st.text_input("Enter a keyword to track:")

if st.button("➕ Add Keyword"):
    if new_word:
        new_word = new_word.strip()
        if new_word in available_keywords:
            if new_word not in st.session_state.selected_keywords:
                if len(st.session_state.selected_keywords) < 4:
                    st.session_state.selected_keywords.append(new_word)
                else:
                    st.warning("You can only track up to 4 keywords.")
            else:
                st.warning("Keyword already added.")
        else:
            st.error(f"'{new_word}' not found in available keywords. Please check spelling.")
    else:
        st.warning("Please type a keyword.")

if st.button("🔁 Clear Keywords"):
    st.session_state.selected_keywords = []

selected_keywords = st.session_state.selected_keywords
st.write("**Current selection:**", selected_keywords)

# Date range selection
min_date, max_date = df.index.min(), df.index.max()
date_range = st.date_input("Select date range", [min_date, max_date])

# Filter data
if selected_keywords:
    filtered = df.loc[date_range[0]:date_range[1], selected_keywords]
else:
    st.warning("Please select at least one keyword.")
    st.stop()

# Visualizations for 1 keyword
if len(selected_keywords) == 1:
    kw = selected_keywords[0]
    st.header(f"📈 Deep Dive: {kw}")

    # 1. Line chart
    st.subheader("1. Trend Over Time")
    fig1 = px.line(filtered, y=kw, title=f"{kw} Search Trend Over Time")
    st.plotly_chart(fig1)

    # 2. Rolling average
    st.subheader("2. 7-Day Rolling Average")
    rolling = filtered[kw].rolling(window=7).mean()
    st.line_chart(rolling)

    # 3. Area chart (cumulative)
    st.subheader("3. Cumulative Interest")
    st.area_chart(filtered[kw].cumsum())

    # 4. Box plot by week
    st.subheader("4. Weekly Popularity Distribution")
    temp = filtered.copy()
    temp["week"] = temp.index.to_period("W")
    fig4 = px.box(temp, x="week", y=kw, title=f"Weekly Interest for {kw}")
    st.plotly_chart(fig4)

    # 5. Heatmap by day of week
    st.subheader("5. Average Popularity by Day of Week")
    temp["day"] = temp.index.day_name()
    heat_avg = temp.groupby("day")[kw].mean().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ])
    st.bar_chart(heat_avg)

# Visualizations for 2–4 keywords
elif 2 <= len(selected_keywords) <= 4:
    st.header("📊 Multi-Keyword Comparison")

    # 1. Line chart
    st.subheader("1. Trend Over Time")
    st.line_chart(filtered)

    # 2. Average popularity bar
    st.subheader("2. Average Popularity per Keyword")
    avg_pop = filtered.mean().reset_index()
    avg_pop.columns = ["keyword", "average"]
    fig2 = px.bar(avg_pop, x="keyword", y="average", title="Average Interest")
    st.plotly_chart(fig2)

    # 3. Cumulative interest
    st.subheader("3. Cumulative Interest Comparison")
    st.line_chart(filtered.cumsum())

    # 4. Distribution (box plot)
    st.subheader("4. Popularity Distribution")
    box_df = filtered.reset_index().melt(id_vars="date", var_name="keyword", value_name="popularity")
    fig4 = px.box(box_df, x="keyword", y="popularity", title="Interest Distribution")
    st.plotly_chart(fig4)

    # 5. Correlation heatmap
    st.subheader("5. Keyword Correlation")
    st.dataframe(filtered.corr().style.background_gradient(cmap="YlGnBu"))

# More than 4?
else:
    st.warning("Please select no more than 4 keywords for analysis.")
