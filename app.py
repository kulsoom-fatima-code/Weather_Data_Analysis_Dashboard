import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(page_title="Historical Weather Analysis", page_icon="🌦️", layout="wide")

DATA_PATH = Path(__file__).parent / "weather_data.csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    if "Formatted Date" in data.columns:
        data["Formatted Date"] = pd.to_datetime(data["Formatted Date"], errors="coerce", utc=True)
        # Keep a timezone-naive timestamp for filtering and plotting
        data["Formatted Date"] = data["Formatted Date"].dt.tz_convert(None)
    return data

st.title("Historical Weather Data Analysis")
st.write("Explore historical weather patterns through interactive filters, summary metrics and visualizations.")

if not DATA_PATH.exists():
    st.error("Dataset not found. Place the downloaded CSV in this project folder and name it exactly weather_data.csv.")
    st.info("Expected file: " + str(DATA_PATH))
    st.stop()

df = load_data(str(DATA_PATH))
if df.empty:
    st.error("The CSV file is empty.")
    st.stop()

date_col = "Formatted Date" if "Formatted Date" in df.columns else None
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# Sidebar filters
st.sidebar.header("Dashboard Filters")
filtered = df.copy()

if date_col and df[date_col].notna().any():
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    selected_dates = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start, end = selected_dates
        filtered = filtered[
            filtered[date_col].dt.date.between(start, end)
        ]

category_filter = None
for candidate in ["Precip Type", "Summary"]:
    if candidate in filtered.columns:
        options = sorted(filtered[candidate].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect(f"Filter by {candidate}", options, default=options)
        if selected:
            filtered = filtered[filtered[candidate].astype(str).isin(selected)]
        category_filter = candidate
        break

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Preferred weather columns
temp = "Temperature (C)" if "Temperature (C)" in filtered.columns else None
humidity = "Humidity" if "Humidity" in filtered.columns else None
wind = "Wind Speed (km/h)" if "Wind Speed (km/h)" in filtered.columns else None
rain = next((c for c in filtered.columns if "rain" in c.lower() or "precip" in c.lower()), None)

def mean_text(col, suffix=""):
    return f"{filtered[col].mean():.2f}{suffix}" if col and pd.to_numeric(filtered[col], errors="coerce").notna().any() else "N/A"

def max_text(col, suffix=""):
    return f"{filtered[col].max():.2f}{suffix}" if col and pd.to_numeric(filtered[col], errors="coerce").notna().any() else "N/A"

m1, m2, m3, m4 = st.columns(4)
m1.metric("Average temperature", mean_text(temp, " °C"))
m2.metric("Highest temperature", max_text(temp, " °C"))
m3.metric("Average humidity", mean_text(humidity))
m4.metric("Records / days", f"{len(filtered):,}")

st.divider()
st.subheader("Weather visualizations")
left, right = st.columns(2)

with left:
    if temp:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(filtered[temp].dropna(), bins=30, kde=True, ax=ax)
        ax.set(title="Temperature distribution", xlabel="Temperature (°C)", ylabel="Frequency")
        st.pyplot(fig)
        plt.close(fig)
    elif numeric_cols:
        col = numeric_cols[0]
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(filtered[col].dropna(), bins=30, kde=True, ax=ax)
        ax.set(title=f"{col} distribution", xlabel=col, ylabel="Frequency")
        st.pyplot(fig)
        plt.close(fig)

with right:
    if temp and humidity:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.scatterplot(data=filtered, x=temp, y=humidity, alpha=0.35, ax=ax)
        ax.set(title="Temperature vs humidity", xlabel="Temperature (°C)", ylabel="Humidity")
        st.pyplot(fig)
        plt.close(fig)
    elif len(numeric_cols) >= 2:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.scatterplot(data=filtered, x=numeric_cols[0], y=numeric_cols[1], alpha=0.35, ax=ax)
        ax.set(title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
        st.pyplot(fig)
        plt.close(fig)

if date_col and temp:
    st.subheader("Temperature trend over time")
    trend = filtered[[date_col, temp]].dropna().sort_values(date_col).copy()
    # Resample dense hourly records to monthly averages for a readable chart
    if len(trend) > 500:
        trend = trend.set_index(date_col)[temp].resample("MS").mean().reset_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(trend[date_col], trend[temp], linewidth=1.5)
    ax.set(title="Temperature over time", xlabel="Date", ylabel="Temperature (°C)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

if humidity and wind:
    st.subheader("Wind speed vs humidity")
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.scatterplot(data=filtered, x=wind, y=humidity, alpha=0.3, ax=ax)
    ax.set(title="Wind speed and humidity", xlabel="Wind speed (km/h)", ylabel="Humidity")
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Correlation heatmap")
corr_cols = filtered.select_dtypes(include=np.number).columns.tolist()
if len(corr_cols) >= 2:
    corr = filtered[corr_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=len(corr_cols) <= 8, fmt=".2f", ax=ax)
    ax.set_title("Correlation between numerical weather variables")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("At least two numeric columns are required for a correlation heatmap.")

st.subheader("Precipitation / weather category comparison")
category_col = "Precip Type" if "Precip Type" in filtered.columns else ("Summary" if "Summary" in filtered.columns else None)
if category_col:
    counts = filtered[category_col].fillna("Unknown").astype(str).value_counts().head(12)
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(x=counts.values, y=counts.index, ax=ax)
    ax.set(title=f"Records by {category_col}", xlabel="Number of records", ylabel=category_col)
    st.pyplot(fig)
    plt.close(fig)
elif wind:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered, y=wind, ax=ax)
    ax.set(title="Wind speed spread", ylabel="Wind speed (km/h)")
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Main findings")
if temp:
    st.write(f"- The average temperature in the selected period is **{filtered[temp].mean():.2f} °C**.")
    st.write(f"- The observed temperature range is **{filtered[temp].min():.2f} °C to {filtered[temp].max():.2f} °C**.")
if humidity:
    st.write(f"- Average humidity is **{filtered[humidity].mean():.3f}**.")
if wind:
    st.write(f"- Average wind speed is **{filtered[wind].mean():.2f} km/h**.")
if temp and humidity:
    corr_value = filtered[[temp, humidity]].corr().iloc[0, 1]
    st.write(f"- Temperature and humidity have a Pearson correlation of **{corr_value:.3f}** in the filtered data.")

if st.checkbox("Show raw data table"):
    st.dataframe(filtered, use_container_width=True)

st.caption("Note: This UK weather dataset does not contain a country/place column. Category filters are used instead of a location filter.")
