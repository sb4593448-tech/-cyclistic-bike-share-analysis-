"""
CYCLISTIC CAPSTONE — ANALYSIS SCRIPT FOR UPLOADED SAMPLE FILE
================================================================
Input: 1789096586745_cyclistic_sample.csv (50 rows, Jan 1-3 2023)

IMPORTANT: This file is a small synthetic/sample dataset, not a full
real-world extract. It is useful for validating the pipeline logic,
but NOT statistically representative. See the case study's
"Data Limitations" section before drawing business conclusions.

To run this analysis on real, full-scale Divvy data instead, use
cyclistic_colab_script.py (streams 12 months directly from S3).
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="Set2")
COLORS = {"member": "#2E86AB", "casual": "#F26419"}

# ============================================================
# PREPARE & PROCESS
# ============================================================
df = pd.read_csv("cyclistic_sample.csv")

df["started_at"] = pd.to_datetime(df["started_at"])
df["ended_at"] = pd.to_datetime(df["ended_at"])

# Data quality checks
print("Shape:", df.shape)
print("Nulls:\n", df.isna().sum())
print("Duplicate ride_id:", df["ride_id"].duplicated().sum())
print("Date range:", df["started_at"].min(), "to", df["started_at"].max())

# Feature engineering
df["ride_length_min"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
df["day_of_week"] = df["started_at"].dt.day_name()
df["month"] = df["started_at"].dt.month_name()
df["hour"] = df["started_at"].dt.hour

# Remove invalid rides (none found in this sample, but kept for pipeline consistency)
df = df[df["ride_length_min"] > 0]
df = df.drop_duplicates(subset="ride_id")

print("\nCleaned shape:", df.shape)

# ============================================================
# ANALYZE
# ============================================================
avg_ride_length = df.groupby("member_casual")["ride_length_min"].agg(["mean", "median", "count"])
print("\n--- Average ride length by user type ---\n", avg_ride_length)

rides_by_day = df.groupby(["day_of_week", "member_casual"]).size().unstack()
print("\n--- Rides by day of week ---\n", rides_by_day)

rides_by_hour = df.groupby(["hour", "member_casual"]).size().unstack()
print("\n--- Rides by hour ---\n", rides_by_hour)

bike_pref = df.groupby(["member_casual", "rideable_type"]).size().unstack()
bike_pref_pct = bike_pref.div(bike_pref.sum(axis=1), axis=0) * 100
print("\n--- Bike type preference (%) ---\n", bike_pref_pct)

# ============================================================
# SHARE — visualizations
# ============================================================
fig, ax = plt.subplots(figsize=(6, 4.5))
avg_ride_length["mean"].reindex(["member", "casual"]).plot(
    kind="bar", color=[COLORS["member"], COLORS["casual"]], ax=ax, width=0.5
)
ax.set_title("Average Ride Duration: Member vs. Casual", fontsize=13, weight="bold")
ax.set_ylabel("Minutes")
ax.set_xticklabels(["Member", "Casual"], rotation=0)
plt.tight_layout()
plt.savefig("sample_chart1_avg_duration.png", dpi=200)
plt.show()

fig, ax = plt.subplots(figsize=(7, 4.5))
rides_by_day.reindex(["Sunday", "Monday", "Tuesday", "Wednesday",
                       "Thursday", "Friday", "Saturday"]).dropna(how="all").plot(
    kind="bar", ax=ax, color=[COLORS["casual"], COLORS["member"]], width=0.7
)
ax.set_title("Total Rides by Day of Week", fontsize=13, weight="bold")
ax.set_ylabel("Rides")
ax.legend(title="Rider Type")
plt.tight_layout()
plt.savefig("sample_chart2_by_day.png", dpi=200)
plt.show()

fig, ax = plt.subplots(figsize=(8, 4.5))
rides_by_hour.plot(kind="line", marker="o", ax=ax, color=[COLORS["casual"], COLORS["member"]])
ax.set_title("Rides by Hour of Day", fontsize=13, weight="bold")
ax.set_ylabel("Rides")
ax.set_xlabel("Hour")
ax.legend(title="Rider Type")
plt.tight_layout()
plt.savefig("sample_chart3_hourly.png", dpi=200)
plt.show()

fig, ax = plt.subplots(figsize=(6, 4.5))
bike_pref_pct.reindex(["member", "casual"]).plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
ax.set_title("Bike Type Preference by User Type", fontsize=13, weight="bold")
ax.set_ylabel("% of Rides")
ax.set_xticklabels(["Member", "Casual"], rotation=0)
ax.legend(title="Bike Type", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("sample_chart4_bike_type.png", dpi=200)
plt.show()

print("\nDone. Charts saved as PNGs.")
