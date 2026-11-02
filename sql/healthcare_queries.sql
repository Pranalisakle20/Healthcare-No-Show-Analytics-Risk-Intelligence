-- ========================================================
-- HEALTHCARE APPOINTMENT NO-SHOW ANALYTICS - SQL SCRIPTS
-- Database: PostgreSQL / MySQL / SQL Server Compatible
-- ========================================================

-- 1. Table DDL Creation
DROP TABLE IF EXISTS appointments_staging;
CREATE TABLE appointments_staging (
    patient_id BIGINT,
    appointment_id BIGINT PRIMARY KEY,
    gender VARCHAR(5),
    scheduled_day TIMESTAMP,
    appointment_day TIMESTAMP,
    age INT,
    neighbourhood VARCHAR(100),
    scholarship INT,
    hypertension INT,
    diabetes INT,
    alcoholism INT,
    handcap INT,
    sms_received INT,
    no_show VARCHAR(5)
);

-- 2. Data Cleaning & Feature Transformation View
CREATE OR REPLACE VIEW v_healthcare_appointments_cleaned AS
SELECT 
    patient_id,
    appointment_id,
    gender,
    age,
    CASE 
        WHEN age < 12 THEN 'Child (0-11)'
        WHEN age BETWEEN 12 AND 18 THEN 'Adolescent (12-18)'
        WHEN age BETWEEN 19 AND 35 THEN 'Young Adult (19-35)'
        WHEN age BETWEEN 36 AND 60 THEN 'Middle-Aged (36-60)'
        ELSE 'Senior (60+)'
    END AS age_group,
    neighbourhood,
    scholarship,
    hypertension,
    diabetes,
    alcoholism,
    handcap,
    (hypertension + diabetes + alcoholism + CASE WHEN handcap > 0 THEN 1 ELSE 0 END) AS total_comorbidities,
    sms_received,
    scheduled_day,
    appointment_day,
    DATE(scheduled_day) AS scheduled_date,
    DATE(appointment_day) AS appointment_date,
    -- Waiting lead time in days
    GREATEST(0, (DATE(appointment_day) - DATE(scheduled_day))) AS lead_days,
    CASE 
        WHEN (DATE(appointment_day) - DATE(scheduled_day)) = 0 THEN 'Same Day'
        WHEN (DATE(appointment_day) - DATE(scheduled_day)) BETWEEN 1 AND 3 THEN 'Short Notice (1-3 d)'
        WHEN (DATE(appointment_day) - DATE(scheduled_day)) BETWEEN 4 AND 14 THEN 'Medium Notice (4-14 d)'
        ELSE 'Long Notice (>14 d)'
    END AS lead_time_category,
    TO_CHAR(appointment_day, 'Day') AS appointment_weekday,
    CASE 
        WHEN no_show = 'Yes' THEN 1 
        ELSE 0 
    END AS is_no_show
FROM appointments_staging
WHERE age >= 0 AND age <= 115
  AND DATE(appointment_day) >= DATE(scheduled_day);

-- 3. Business Aggregation Query 1: Overall KPI Summary
SELECT 
    COUNT(*) AS total_appointments,
    COUNT(DISTINCT patient_id) AS unique_patients,
    SUM(is_no_show) AS total_no_shows,
    ROUND(AVG(is_no_show) * 100.0, 2) AS overall_no_show_rate_pct,
    ROUND(AVG(lead_days), 1) AS avg_lead_days,
    ROUND(AVG(age), 1) AS avg_patient_age
FROM v_healthcare_appointments_cleaned;

-- 4. Business Aggregation Query 2: Impact of SMS Reminder on No-Show Rate
SELECT 
    sms_received,
    CASE WHEN sms_received = 1 THEN 'SMS Sent' ELSE 'No SMS' END AS reminder_status,
    COUNT(*) AS total_booked,
    SUM(is_no_show) AS no_shows,
    ROUND(AVG(is_no_show) * 100.0, 2) AS no_show_rate_pct
FROM v_healthcare_appointments_cleaned
GROUP BY sms_received
ORDER BY sms_received DESC;

-- 5. Business Aggregation Query 3: Lead Days vs No-Show Rate
SELECT 
    lead_time_category,
    COUNT(*) AS total_appointments,
    SUM(is_no_show) AS no_shows,
    ROUND(AVG(is_no_show) * 100.0, 2) AS no_show_rate_pct
FROM v_healthcare_appointments_cleaned
GROUP BY lead_time_category
ORDER BY no_show_rate_pct DESC;

-- 6. Business Aggregation Query 4: Top 10 High-Risk Neighbourhoods (>200 appointments)
SELECT 
    neighbourhood,
    COUNT(*) AS total_appointments,
    SUM(is_no_show) AS no_shows,
    ROUND(AVG(is_no_show) * 100.0, 2) AS no_show_rate_pct
FROM v_healthcare_appointments_cleaned
GROUP BY neighbourhood
HAVING COUNT(*) >= 200
ORDER BY no_show_rate_pct DESC
LIMIT 10;

-- 7. Business Aggregation Query 5: Chronic Condition Risk Profile
SELECT 
    hypertension,
    diabetes,
    scholarship,
    COUNT(*) AS total_patients,
    ROUND(AVG(is_no_show) * 100.0, 2) AS no_show_rate_pct
FROM v_healthcare_appointments_cleaned
GROUP BY hypertension, diabetes, scholarship
ORDER BY total_patients DESC;
