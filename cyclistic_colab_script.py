"""
CYCLISTIC BIKE-SHARE CAPSTONE — GOOGLE COLAB SCRIPT
=====================================================
Phases covered: PREPARE, PROCESS, ANALYZE, SHARE (visualizations)

Design goal: never write the raw 12-month dataset to local disk.
Everything is streamed S3 -> BytesIO -> ZipFile -> pandas, in memory.

Run this top-to-bottom in a single Colab notebook.
Estimated runtime: 5-15 min depending on connection speed (~12 zips, ~1-2GB total).
"""

# ============================================================
# 0. SETUP
# ============================================================
!pip install -q requests pandas matplotlib seaborn

import re
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
import xml.etree.ElementTree as ET

sns.set_theme(style="whitegrid", palette="Set2")
pd.set_option("display.max_columns", None)

BUCKET_URL = "https://divvy-tripdata.s3.amazonaws.com/"


# ============================================================
# 1. PREPARE — discover & stream the latest 12 months from S3
# ============================================================

def list_bucket_keys(bucket_url: str = BUCKET_URL) -> list:
    """Parse the public S3 bucket XML listing to get every available file key."""
    resp = requests.get(bucket_url)
    resp.raise_for_status()
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    root = ET.fromstring(resp.content)
    keys = [c.find("s3:Key", ns).text for c in root.findall("s3:Contents", ns)]
    return keys


def get_latest_n_month_files(keys: list, n: int = 12) -> list:
    """
    Filter for files matching YYYYMM-divvy-tripdata.zip, exclude non-monthly
    archives (e.g. quarterly/legacy naming), and return the n most recent
    months in chronological order.
    """
    pattern = re.compile(r"^(\d{6})-divvy-tripdata\.zip$")
    dated = []
    for k in keys:
        m = pattern.match(k)
        if m:
            dated.append((datetime.strptime(m.group(1), "%Y%m"), k))
    dated.sort(reverse=True)
    latest = [k for _, k in dated[:n]]
    return sorted(latest)  # chronological order, oldest -> newest


def load_month_from_s3(key: str, bucket_url: str = BUCKET_URL) -> pd.DataFrame:
    """Stream a single monthly zip into memory and return its CSV as a DataFrame."""
    url = bucket_url + key
    r = requests.get(url)
    r.raise_for_status()
    with ZipFile(BytesIO(r.content)) as z:
        csv_names = [
            n for n in z.namelist()
            if n.lower().endswith(".csv") and not n.startswith("__MACOSX")
        ]
        with z.open(csv_names[0]) as f:
            df = pd.read_csv(f, low_memory=False)
    return df


print("Fetching bucket file listing...")
all_keys = list_bucket_keys()
latest_12 = get_latest_n_month_files(all_keys, n=12)
print(f"Selected {len(latest_12)} monthly files:")
for k in latest_12:
    print(" -", k)

frames = []
for key in latest_12:
    print(f"Streaming {key} ...")
    frames.append(load_month_from_s3(key))

df = pd.concat(frames, ignore_index=True)
del frames  # free memory
print(f"\nCombined raw dataset shape: {df.shape}")
print(df.dtypes)


# ============================================================
# 2. PROCESS — clean, transform, engineer features
# ============================================================

# a) Parse datetimes
df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
df["ended_at"] = pd.to_datetime(df["ended_at"], errors="coerce")

# Drop rows with unparseable timestamps or missing critical keys
df = df.dropna(subset=["started_at", "ended_at", "ride_id", "member_casual", "rideable_type"])

# b) Ride length in minutes
df["ride_length_min"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60

# c) Day-of-week / month / hour features
df["day_of_week"] = df["started_at"].dt.day_name()
df["month"] = df["started_at"].dt.month_name()
df["month_num"] = df["started_at"].dt.month
df["hour"] = df["started_at"].dt.hour
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"])

# d) Remove negative/zero ride lengths and extreme outliers (> 24h, likely
#    docking errors or maintenance holds rather than genuine rides)
before = len(df)
df = df[(df["ride_length_min"] > 0) & (df["ride_length_min"] < 1440)]
print(f"Removed {before - len(df):,} rows with invalid ride_length.")

# e) Filter out system/test/maintenance rides (station names flagged as test/repair)
test_pattern = r"test|repair|divvy.*staff|maintenance"
station_cols = [c for c in ["start_station_name", "end_station_name"] if c in df.columns]
test_mask = pd.Series(False, index=df.index)
for col in station_cols:
    test_mask |= df[col].astype(str).str.contains(test_pattern, case=False, na=False, regex=True)
before = len(df)
df = df[~test_mask]
print(f"Removed {before - len(df):,} rows flagged as test/maintenance rides.")

# Drop exact duplicate ride_ids
df = df.drop_duplicates(subset="ride_id")

print(f"\nFinal cleaned dataset shape: {df.shape}")
print(df["member_casual"].value_counts())

# Optional memory optimization for large frames
for col in ["member_casual", "rideable_type", "day_of_week", "month"]:
    df[col] = df[col].astype("category")

# Sanity check
print("\nMissing values per column (top 10):")
print(df.isna().sum().sort_values(ascending=False).head(10))


# ============================================================
# 3. ANALYZE — summary statistics, member vs. casual comparison
# ============================================================

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# a) Average ride length by user type
avg_ride_length = df.groupby("member_casual", observed=True)["ride_length_min"].agg(
    ["mean", "median", "count"]
).round(2)
print("\n--- Average ride length by user type (minutes) ---")
print(avg_ride_length)

# b) Total rides by user type x day of week, and x month
rides_by_day = (
    df.groupby(["day_of_week", "member_casual"], observed=True)
    .size()
    .unstack("member_casual")
    .reindex(DAY_ORDER)
)
print("\n--- Rides by day of week ---")
print(rides_by_day)

rides_by_month = (
    df.groupby(["month", "member_casual"], observed=True)
    .size()
    .unstack("member_casual")
    .reindex(MONTH_ORDER)
)
print("\n--- Rides by month ---")
print(rides_by_month)

# c) Bike type preference by user type
bike_pref = (
    df.groupby(["member_casual", "rideable_type"], observed=True)
    .size()
    .unstack("rideable_type")
)
bike_pref_pct = bike_pref.div(bike_pref.sum(axis=1), axis=0).round(3) * 100
print("\n--- Bike type preference (% within user type) ---")
print(bike_pref_pct)

# d) Peak hourly demand by user type
hourly_demand = (
    df.groupby(["hour", "member_casual"], observed=True)
    .size()
    .unstack("member_casual")
)
print("\n--- Rides by hour of day ---")
print(hourly_demand)

# Weekday vs weekend average ride length (useful for the "Act" narrative)
weekend_avg = df.groupby(["member_casual", "is_weekend"], observed=True)["ride_length_min"].mean().round(2)
print("\n--- Avg ride length: weekday vs weekend ---")
print(weekend_avg)


# ============================================================
# 4. SHARE — publication-ready visualizations
# ============================================================

COLORS = {"member": "#2E86AB", "casual": "#F26419"}

# --- Chart 1: Average ride duration, casual vs member ---
fig, ax = plt.subplots(figsize=(7, 5))
avg_ride_length["mean"].reindex(["member", "casual"]).plot(
    kind="bar", color=[COLORS["member"], COLORS["casual"]], ax=ax, width=0.5
)
ax.set_title("Average Ride Duration: Member vs. Casual Rider", fontsize=14, weight="bold")
ax.set_xlabel("")
ax.set_ylabel("Average Ride Length (minutes)")
ax.set_xticklabels(["Member", "Casual"], rotation=0)
for i, v in enumerate(avg_ride_length["mean"].reindex(["member", "casual"])):
    ax.text(i, v + 0.3, f"{v:.1f} min", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig("chart1_avg_ride_duration.png", dpi=200)
plt.show()

# --- Chart 2: Total rides by day of week ---
fig, ax = plt.subplots(figsize=(9, 5))
rides_by_day.plot(kind="bar", ax=ax, color=[COLORS["casual"], COLORS["member"]], width=0.75)
ax.set_title("Total Rides by Day of Week: Weekday vs. Weekend Behavior", fontsize=14, weight="bold")
ax.set_xlabel("")
ax.set_ylabel("Number of Rides")
ax.legend(title="Rider Type")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart2_rides_by_day.png", dpi=200)
plt.show()

# --- Chart 3: Monthly ride trends ---
fig, ax = plt.subplots(figsize=(10, 5))
rides_by_month.plot(kind="line", marker="o", ax=ax, color=[COLORS["casual"], COLORS["member"]], linewidth=2.5)
ax.set_title("Monthly Ride Trends Throughout the Year", fontsize=14, weight="bold")
ax.set_xlabel("")
ax.set_ylabel("Number of Rides")
ax.legend(title="Rider Type")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart3_monthly_trends.png", dpi=200)
plt.show()

# --- Chart 4: Preferred bike types by user type ---
fig, ax = plt.subplots(figsize=(8, 5))
bike_pref_pct.reindex(["member", "casual"]).plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
ax.set_title("Preferred Bike Types by User Type", fontsize=14, weight="bold")
ax.set_xlabel("")
ax.set_ylabel("Share of Rides (%)")
ax.set_xticklabels(["Member", "Casual"], rotation=0)
ax.legend(title="Bike Type", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("chart4_bike_type_preference.png", dpi=200)
plt.show()

# Bonus: hourly demand curve (useful supporting chart for the deck)
fig, ax = plt.subplots(figsize=(10, 5))
hourly_demand.plot(kind="line", marker="o", ax=ax, color=[COLORS["casual"], COLORS["member"]])
ax.set_title("Hourly Ride Demand: Member vs. Casual", fontsize=14, weight="bold")
ax.set_xlabel("Hour of Day (24h)")
ax.set_ylabel("Number of Rides")
ax.legend(title="Rider Type")
plt.tight_layout()
plt.savefig("chart5_hourly_demand.png", dpi=200)
plt.show()


# ============================================================
# 5. EXPORT SUMMARY TABLES (small, aggregated — safe to download)
# ============================================================
# NOTE: we only export aggregated summary tables, not the raw multi-GB
# dataset, keeping everything lightweight enough for Tableau Public.

avg_ride_length.to_csv("summary_avg_ride_length.csv")
rides_by_day.to_csv("summary_rides_by_day.csv")
rides_by_month.to_csv("summary_rides_by_month.csv")
bike_pref_pct.to_csv("summary_bike_type_pct.csv")
hourly_demand.to_csv("summary_hourly_demand.csv")

# In Colab, trigger local downloads with:
# from google.colab import files
# for f in ["summary_avg_ride_length.csv", "summary_rides_by_day.csv",
#           "summary_rides_by_month.csv", "summary_bike_type_pct.csv",
#           "summary_hourly_demand.csv"]:
#     files.download(f)

print("\nDone. Summary CSVs are ready for Tableau / Sheets import.")
print("Fill the actual printed values into the case study write-up before publishing.")
