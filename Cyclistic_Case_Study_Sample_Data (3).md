# Cyclistic Bike-Share Case Study: Converting Casual Riders into Annual Members

*A Google Data Analytics Capstone Project*

> **⚠️ A note on this dataset, read before publishing:** The uploaded file (`cyclistic_sample.csv`) contains only **50 rides spanning 3 calendar days** (Jan 1–3, 2023), in a perfectly alternating synthetic pattern — every casual ride is exactly 30 minutes on a `classic_bike`, and every member ride is exactly 30 minutes on an `electric_bike`, one hour apart. This is almost certainly a **pipeline test/sample file**, not a real operational extract. The numbers below are computed honestly from this file — nothing is fabricated — but they describe the sample's structure, not genuine Cyclistic rider behavior. Treat this as a **proof-of-concept run of the full analysis pipeline**, and re-run the same code against the full 12-month Divvy dataset (via `cyclistic_colab_script.py` from the earlier deliverable) before using any conclusion for real marketing decisions.

---

## 1. Introduction

Cyclistic is a Chicago-based bike-share program offering three pricing options: single-ride passes, full-day passes, and annual memberships. Riders on single-ride/day passes are **casual riders**; riders on annual plans are **members**. Cyclistic's Director of Marketing, **Lily Moreno**, believes the fastest path to profitable growth is converting existing casual riders into annual members, rather than pursuing entirely new customers.

---

## 2. Ask Phase

### Business Task
Analyze Cyclistic trip data to determine how annual members and casual riders use the bike-share service differently, then translate those differences into concrete, data-backed recommendations to convert casual riders into members.

### Key Business Questions
1. How do annual members and casual riders use Cyclistic bikes differently?
2. Why would casual riders buy an annual membership?
3. How can Cyclistic use digital marketing to influence casual riders to convert?

### Stakeholders
| Stakeholder | Role |
|---|---|
| **Lily Moreno** | Director of Marketing — owns the strategic direction of the conversion campaign |
| **Marketing Analytics Team** | Responsible for collecting, cleaning, analyzing, and reporting on trip data |
| **Executive Team** | Reviews and approves the final marketing recommendations |

---

## 3. Prepare Phase

**Data source:** `cyclistic_sample.csv`, a 50-row extract with columns `ride_id`, `rideable_type`, `started_at`, `ended_at`, `member_casual`.

**ROCCC check on this specific file:**
| Criterion | Assessment |
|---|---|
| Reliable | Schema matches Divvy's real trip-data format |
| Original | Source/provenance unclear (uploaded directly by user) |
| Comprehensive | **Fails** — only 50 rows, 3 days, no station or geographic fields |
| Current | Dated Jan 2023 |
| Cited | Not applicable (sample file) |

### Data Limitations (important)
- **Sample size:** 50 rows is far too small for statistically valid behavioral conclusions. Cyclistic's real dataset spans millions of rides per year.
- **Perfect alternation:** Casual and member rides alternate by the hour with zero variance in duration (always exactly 30.0 minutes), which does not resemble real-world ride-time distributions (which are typically right-skewed, with a spread from a few minutes to several hours).
- **No station data:** `start_station_name`/`end_station_name` and lat/lng are absent, so no geographic targeting analysis (e.g., top casual-rider stations) is possible here.
- **3-day window:** No seasonality or weekly-pattern signal can be extracted — the "day of week" comparison below is really just 3 discrete days, not a real weekly cycle.

**Conclusion:** this file should be treated as a **schema/pipeline validation sample**. All structural findings below are accurate *for this file*, but should not be generalized to real Cyclistic ridership without re-running on the full dataset.

---

## 4. Process Phase

Cleaning steps applied (see `cyclistic_sample_analysis.py`):

1. Parsed `started_at`/`ended_at` as datetimes.
2. Calculated `ride_length_min`.
3. Engineered `day_of_week`, `month`, `hour`.
4. Checked for nulls, duplicate `ride_id`, and invalid (≤0 minute) ride lengths.

**Results of the quality checks:**
- Rows: 50 → 50 (no rows dropped — data was already clean)
- Missing values: 0 across all columns
- Duplicate `ride_id`: 0
- Invalid (≤0 min) ride lengths: 0
- Date range: **2023-01-01 00:00:00 to 2023-01-03 01:00:00**

---

## 5. Analyze Phase

### Summary Statistics (computed directly from the uploaded file)

| Metric | Member | Casual |
|---|---|---|
| Average ride length | 30.0 min | 30.0 min |
| Median ride length | 30.0 min | 30.0 min |
| Total rides | 25 | 25 |
| Bike type used | 100% `electric_bike` | 100% `classic_bike` |
| Rides on Sunday | 12 | 12 |
| Rides on Monday | 12 | 12 |
| Rides on Tuesday | 1 | 1 |

### Analysis Code
```python
avg_ride_length = df.groupby("member_casual")["ride_length_min"].agg(["mean", "median", "count"])
rides_by_day = df.groupby(["day_of_week", "member_casual"]).size().unstack()
rides_by_hour = df.groupby(["hour", "member_casual"]).size().unstack()
bike_pref = df.groupby(["member_casual", "rideable_type"]).size().unstack()
```
(Full script: `cyclistic_sample_analysis.py`)

### Key Insights (from this sample only)

- **Ride duration is identical and constant (30 min) for both groups** — in this sample there is no duration-based behavioral difference to act on, which is itself a strong signal this is synthetic test data rather than organic usage.
- **Bike type is a perfect 100%/0% split** — every casual ride used a `classic_bike`, every member ride used an `electric_bike`. In real data this would be a striking finding; here it's more likely an artifact of how the sample rows were generated.
- **Rides alternate by the hour** — casual rides fall on even hours (0, 2, 4, 6...), member rides on odd hours (1, 3, 5, 7...), producing a perfectly interleaved hourly pattern rather than a realistic commute-vs-leisure curve.
- **Equal volume, no weekly pattern** — casual and member counts are tied on every single day (12/12, 12/12, 1/1), so there is no weekday-vs-weekend skew to report, unlike what you'd expect (and what we projected) in the full 12-month analysis.

---

## 6. Share Phase — Visualizations

Four charts generated directly from this file (`cyclistic_sample_analysis.py`):

1. **`sample_chart1_avg_duration.png`** — confirms the flat 30/30 minute comparison
2. **`sample_chart2_by_day.png`** — shows the tied Sunday/Monday/Tuesday counts
3. **`sample_chart3_hourly.png`** — shows the alternating even/odd-hour pattern
4. **`sample_chart4_bike_type.png`** — shows the 100% classic vs. 100% electric split

### Dashboard note
Because this sample lacks station-level and month-level variety, a Tableau dashboard built from it would visually confirm the pipeline works (charts render, colors/legends are correct) but would **not** contain a real story to present to Lily Moreno. Rebuild the dashboard once the full-year dataset summary CSVs (from `cyclistic_colab_script.py`) are available — the dashboard-build steps from that deliverable apply unchanged.

---

## 7. Act Phase — Recommendations

Given the data limitation above, these recommendations are framed as **hypotheses to validate on the full dataset**, not final conclusions — which is itself good analytical practice: don't let a 50-row sample drive real budget decisions.

1. **Re-run this exact pipeline on the full 12-month dataset before acting on anything.** The sample confirms the code works end-to-end (cleaning, aggregation, charting); the next step is pointing it at real volume so the insights are trustworthy.
2. **If a genuine bike-type split emerges in the full data** (e.g., members favoring electric bikes for speed/reliability on commutes), consider bundling electric-bike access or reduced e-bike unlock fees into the membership pitch — this sample's 100% split is a useful hypothesis to test, even though it's an artifact here.
3. **Once weekday/weekend and seasonal patterns are visible in the full data**, target conversion campaigns at the specific days/months where casual ridership spikes (as outlined in the earlier full-pipeline case study) rather than running a flat, always-on campaign.
4. **Request full-resolution data with station fields** from your data source. Station-level fields (`start_station_name`, lat/lng) are essential for the geo-targeted marketing recommendation (station-adjacent ads, QR sign-up prompts) — this sample file doesn't include them, so that piece of the strategy can't be validated yet.

---

## 8. Appendix

- **Analysis script for this file:** `cyclistic_sample_analysis.py`
- **Charts:** `sample_chart1_avg_duration.png`, `sample_chart2_by_day.png`, `sample_chart3_hourly.png`, `sample_chart4_bike_type.png`
- **Summary tables:** `sample_summary_avg_length.csv`, `sample_summary_by_day.csv`, `sample_summary_by_hour.csv`, `sample_summary_bike_pct.csv`
- **For real, full-scale analysis:** use `cyclistic_colab_script.py` (streams 12 months of real Divvy data from S3) and `cyclistic_sql_queries.sql` (BigQuery companion queries) from the earlier deliverable.

---

*Prepared as part of the Google Data Analytics Professional Certificate Capstone Project. This version documents a pipeline-validation run on a small sample file — see the companion full-scale case study for a production-ready analysis built on real 12-month Divvy trip data.*
