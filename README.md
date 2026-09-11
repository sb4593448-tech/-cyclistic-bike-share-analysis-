# 🚲 Cyclistic Bike-Share Capstone: Converting Casual Riders into Annual Members

**Google Data Analytics Professional Certificate — Capstone Project**

Analyzing 12 months of Divvy bike-share trip data to understand how annual members and casual riders use Cyclistic differently, and translating that into a data-driven marketing strategy to convert casual riders into members.

---

## 📌 Business Task

Cyclistic's Director of Marketing, Lily Moreno, believes the fastest path to sustainable growth is converting existing **casual riders** into **annual members**, rather than acquiring entirely new customers. This project analyzes historical trip data to identify the behavioral differences between the two rider types and turns those findings into concrete marketing recommendations.

**Full write-up:** [`Cyclistic_Case_Study.md`](./Cyclistic_Case_Study.md)

---

## 🗂️ Repo Structure

| File | Description |
|---|---|
| `Cyclistic_Case_Study.md` | Full portfolio case study — all 6 phases (Ask → Act), production-ready |
| `Cyclistic_Case_Study_Sample_Data.md` | Pipeline-validation run on a small sample file, with data-limitation notes |
| `cyclistic_colab_script.py` | Full pipeline: streams 12 months of real Divvy data from S3, cleans, analyzes, visualizes — runs entirely in memory, no local raw-data storage |
| `cyclistic_sample_analysis.py` | Same pipeline logic, adapted for a local sample CSV |
| `Cyclistic_Capstone_Kaggle_Colab.ipynb` | Notebook version of the full pipeline, ready for Kaggle or Colab |
| `cyclistic_sql_queries.sql` | BigQuery-syntax companion queries mirroring the pandas analysis |
| `sample_chart*.png` | Charts generated from the pipeline-validation run |

---

## 🔧 Tools Used

- **Python** — pandas, requests, matplotlib, seaborn
- **Google Colab** — cloud execution, no local storage of raw data
- **BigQuery** (optional) — SQL-based analysis path
- **Tableau Public** — dashboard and visualization

---

## 📊 Process Summary

1. **Ask** — Defined the business task and stakeholders (Lily Moreno, Marketing Analytics Team, Executive Team).
2. **Prepare** — Streamed the latest 12 months of trip data directly from the [Divvy S3 bucket](https://divvy-tripdata.s3.amazonaws.com/index.html) into memory.
3. **Process** — Parsed timestamps, engineered `ride_length`, `day_of_week`, `month`, `hour`; removed invalid/test rides.
4. **Analyze** — Compared ride duration, weekly/monthly patterns, bike-type preference, and hourly demand between members and casual riders.
5. **Share** — Built four core visualizations and a Tableau Public dashboard.
6. **Act** — Delivered 4 targeted marketing recommendations to convert casual riders into members.

## 🎯 Key Recommendation Highlights

See [`Cyclistic_Case_Study.md`](./Cyclistic_Case_Study.md#7-act-phase--recommendations) for the full reasoning behind each. In short: target weekend/leisure casual riders with a trial membership, concentrate campaigns during peak casual-usage months, geo-target high-traffic casual stations, and reframe membership value around commute-cost savings.

## 📈 Dashboard


`[file:///C:/Users/MUHAMMAD%20QASIM/Downloads/index.html]`

---

## ▶️ How to Reproduce

1. Open `Cyclistic_Capstone_Kaggle_Colab.ipynb` in Google Colab or Kaggle.
2. Run all cells top to bottom — this streams the 12 latest months from S3, cleans and analyzes the data, and generates all four charts.
3. (Optional) Load cleaned data into BigQuery and run `cyclistic_sql_queries.sql` for a SQL-based cross-check.
4. Export the small aggregated summary CSVs and build the dashboard in Tableau Public.

---

## 👤 Author

**Sadiqa Bibi** Cyberpsychology researcher exploring the intersection of Psychology, Data & AI LinkedIn: [https://www.linkedin.com/in/sadiqa-cyberpsych/]


*This project was completed as part of the Google Data Analytics Professional Certificate capstone.*
