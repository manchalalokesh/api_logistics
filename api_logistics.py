import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("APL_Logistics.csv", encoding="latin1")
    df["Days for shipping (real)"] = pd.to_numeric(df["Days for shipping (real)"], errors="coerce")
    df["Days for shipment (scheduled)"] = pd.to_numeric(df["Days for shipment (scheduled)"], errors="coerce")
    df["Order Profit Per Order"] = pd.to_numeric(df["Order Profit Per Order"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Late_delivery_risk"] = pd.to_numeric(df["Late_delivery_risk"], errors="coerce")
    df["Delay_days"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
    return df

df = load_data()

st.title("🚚 Delivery Performance, Delay Risk & Logistics Efficiency")

# ── Sidebar Filters ────────────────────────────────────────
st.sidebar.header("Filters")

shipping_options = ["All"] + sorted(df["Shipping Mode"].dropna().unique().tolist())
selected_shipping = st.sidebar.selectbox("Shipping Mode", shipping_options)

region_options = ["All"] + sorted(df["Order Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", region_options)

market_options = ["All"] + sorted(df["Market"].dropna().unique().tolist())
selected_market = st.sidebar.selectbox("Market", market_options)

segment_options = ["All"] + sorted(df["Customer Segment"].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Customer Segment", segment_options)

# Apply filters
filtered = df.copy()
if selected_shipping != "All":
    filtered = filtered[filtered["Shipping Mode"] == selected_shipping]
if selected_region != "All":
    filtered = filtered[filtered["Order Region"] == selected_region]
if selected_market != "All":
    filtered = filtered[filtered["Market"] == selected_market]
if selected_segment != "All":
    filtered = filtered[filtered["Customer Segment"] == selected_segment]

# ── MODULE 1: Delivery Performance Overview ────────────────
st.header("📦 Module 1: Delivery Performance Overview")

on_time_rate = (filtered["Late_delivery_risk"] == 0).mean() * 100
late_rate = (filtered["Late_delivery_risk"] == 1).mean() * 100
avg_delay = filtered["Delay_days"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("✅ On-Time Delivery Rate", f"{on_time_rate:.1f}%")
col2.metric("⚠️ Late Delivery Risk Ratio", f"{late_rate:.1f}%")
col3.metric("📅 Avg Delivery Delay (Days)", f"{avg_delay:.2f}")

# Delivery Status bar chart
st.subheader("Delivery Status Distribution")
if "Delivery Status" in filtered.columns:
    status_counts = filtered["Delivery Status"].value_counts()
    fig, ax = plt.subplots()
    status_counts.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_xlabel("Delivery Status")
    ax.set_ylabel("Count")
    ax.set_title("Orders by Delivery Status")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ── MODULE 2: Delay Risk Analysis ─────────────────────────
st.header("⚠️ Module 2: Delay Risk Analysis Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Late Delivery Risk Distribution")
    risk_counts = filtered["Late_delivery_risk"].value_counts().rename({0: "On Time", 1: "Late"})
    fig, ax = plt.subplots()
    risk_counts.plot(kind="bar", ax=ax, color=["green", "red"])
    ax.set_ylabel("Count")
    ax.set_title("On Time vs Late")
    plt.xticks(rotation=0)
    st.pyplot(fig)

with col2:
    st.subheader("Delay Gap Histogram")
    fig, ax = plt.subplots()
    filtered["Delay_days"].dropna().hist(bins=30, ax=ax, color="orange", edgecolor="black")
    ax.set_xlabel("Delay Days (Real - Scheduled)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Delivery Delay")
    st.pyplot(fig)

# ── MODULE 3: Shipping Mode Comparison ────────────────────
st.header("🚢 Module 3: Shipping Mode Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Avg Delay by Shipping Mode")
    ship_delay = df.groupby("Shipping Mode")["Delay_days"].mean().sort_values()
    fig, ax = plt.subplots()
    ship_delay.plot(kind="bar", ax=ax, color="purple")
    ax.set_ylabel("Avg Delay (Days)")
    ax.set_title("Mode-wise Delay Performance")
    plt.xticks(rotation=45)
    st.pyplot(fig)

with col2:
    st.subheader("SLA Compliance by Shipping Mode")
    sla = df.groupby("Shipping Mode")["Late_delivery_risk"].apply(
        lambda x: (x == 0).mean() * 100
    ).sort_values(ascending=False)
    fig, ax = plt.subplots()
    sla.plot(kind="bar", ax=ax, color="teal")
    ax.set_ylabel("On-Time Rate (%)")
    ax.set_title("SLA Compliance by Mode")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ── MODULE 4: Regional & Market Heatmaps ──────────────────
st.header("🌍 Module 4: Regional & Market Heatmaps")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Avg Delay by Region")
    region_delay = df.groupby("Order Region")["Delay_days"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 5))
    region_delay.plot(kind="barh", ax=ax, color="coral")
    ax.set_xlabel("Avg Delay (Days)")
    ax.set_title("Regional Delay Index")
    st.pyplot(fig)

with col2:
    st.subheader("Market-wise Logistics Efficiency")
    market_delay = df.groupby("Market")["Delay_days"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 5))
    market_delay.plot(kind="barh", ax=ax, color="skyblue")
    ax.set_xlabel("Avg Delay (Days)")
    ax.set_title("Market Delay Index")
    st.pyplot(fig)

# Heatmap: Region vs Shipping Mode
st.subheader("Heatmap: Avg Delay — Region vs Shipping Mode")
pivot = df.pivot_table(values="Delay_days", index="Order Region", columns="Shipping Mode", aggfunc="mean")
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax)
ax.set_title("Avg Delay Days by Region & Shipping Mode")
st.pyplot(fig)

st.caption("Dashboard — Supply Chain Delivery Analysis")