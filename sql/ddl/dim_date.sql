CREATE TABLE IF NOT EXISTS dim_date (
    date_id         INT PRIMARY KEY,
    date            DATE NOT NULL,
    year            INT,
    quarter         INT,
    month           INT,
    month_name      VARCHAR(20),
    day             INT,
    week_of_year    INT,
    day_of_week     INT,
    day_name        VARCHAR(20),
    is_weekday      BOOLEAN,
    is_weekend      BOOLEAN,
    is_month_start  BOOLEAN,
    is_month_end    BOOLEAN
    
);

INSERT INTO dim_date
WITH dates AS (
    SELECT generate_series(
        DATE '2023-01-01',
        CURRENT_DATE + INTERVAL '1 year',
        INTERVAL '1 day'
    ) AS date
)
SELECT
    TO_CHAR(date, 'YYYYMMDD')::INT AS date_id,
    date,
    EXTRACT(YEAR FROM date)::INT AS year,
    EXTRACT(QUARTER FROM date)::INT AS quarter,
    EXTRACT(MONTH FROM date)::INT AS month,
    TO_CHAR(date, 'Month') AS month_name,
    EXTRACT(DAY FROM date)::INT AS day,
    EXTRACT(WEEK FROM date)::INT AS week_of_year,
    EXTRACT(DOW FROM date)::INT AS day_of_week,
    TO_CHAR(date, 'Day') AS day_name,
    CASE WHEN EXTRACT(DOW FROM date) BETWEEN 1 AND 5 THEN TRUE ELSE FALSE END AS is_weekday,
    CASE WHEN EXTRACT(DOW FROM date) IN (0,6) THEN TRUE ELSE FALSE END AS is_weekend,
    CASE WHEN date = DATE_TRUNC('month', date)::DATE THEN TRUE ELSE FALSE END AS is_month_start,
    CASE 
        WHEN date = (DATE_TRUNC('month', date) + INTERVAL '1 month - 1 day')::DATE 
        THEN TRUE ELSE FALSE
    END AS is_month_end
FROM dates;