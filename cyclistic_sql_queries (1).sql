-- ============================================================
-- CYCLISTIC CAPSTONE — SQL COMPANION QUERIES (BigQuery syntax)
-- ============================================================
-- Assumes cleaned data has been loaded into BigQuery as:
--   `cyclistic_analysis.trips_cleaned`
-- Columns: ride_id, rideable_type, started_at, ended_at,
--          member_casual, ride_length_min, day_of_week, month, hour
--
-- These mirror the pandas analysis in cyclistic_colab_script.py,
-- useful if you prefer to push cleaned data to BigQuery and drive
-- Tableau/Looker Studio off SQL views instead of local CSVs.

-- 1) Average ride length by user type
SELECT
  member_casual,
  ROUND(AVG(ride_length_min), 2) AS avg_ride_length_min,
  ROUND(APPROX_QUANTILES(ride_length_min, 2)[OFFSET(1)], 2) AS median_ride_length_min,
  COUNT(*) AS total_rides
FROM `cyclistic_analysis.trips_cleaned`
GROUP BY member_casual
ORDER BY member_casual;

-- 2) Total rides by user type and day of week
SELECT
  day_of_week,
  member_casual,
  COUNT(*) AS ride_count
FROM `cyclistic_analysis.trips_cleaned`
GROUP BY day_of_week, member_casual
ORDER BY
  CASE day_of_week
    WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
    WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
    WHEN 'Sunday' THEN 7 END,
  member_casual;

-- 3) Total rides by user type and month
SELECT
  month,
  member_casual,
  COUNT(*) AS ride_count
FROM `cyclistic_analysis.trips_cleaned`
GROUP BY month, member_casual
ORDER BY
  CASE month
    WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
    WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
    WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
    WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
  END,
  member_casual;

-- 4) Bike type preference (% share) by user type
WITH counts AS (
  SELECT
    member_casual,
    rideable_type,
    COUNT(*) AS ride_count
  FROM `cyclistic_analysis.trips_cleaned`
  GROUP BY member_casual, rideable_type
),
totals AS (
  SELECT member_casual, SUM(ride_count) AS total_rides
  FROM counts
  GROUP BY member_casual
)
SELECT
  c.member_casual,
  c.rideable_type,
  c.ride_count,
  ROUND(100 * c.ride_count / t.total_rides, 1) AS pct_of_user_type
FROM counts c
JOIN totals t USING (member_casual)
ORDER BY c.member_casual, pct_of_user_type DESC;

-- 5) Peak hourly demand by user type
SELECT
  hour,
  member_casual,
  COUNT(*) AS ride_count
FROM `cyclistic_analysis.trips_cleaned`
GROUP BY hour, member_casual
ORDER BY hour, member_casual;

-- 6) Weekday vs weekend average ride length
SELECT
  member_casual,
  CASE WHEN day_of_week IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
  ROUND(AVG(ride_length_min), 2) AS avg_ride_length_min,
  COUNT(*) AS ride_count
FROM `cyclistic_analysis.trips_cleaned`
GROUP BY member_casual, day_type
ORDER BY member_casual, day_type;

-- 7) Top 10 start stations for casual riders (useful for geo-targeted marketing)
SELECT
  start_station_name,
  COUNT(*) AS casual_ride_count
FROM `cyclistic_analysis.trips_cleaned`
WHERE member_casual = 'casual'
  AND start_station_name IS NOT NULL
GROUP BY start_station_name
ORDER BY casual_ride_count DESC
LIMIT 10;
