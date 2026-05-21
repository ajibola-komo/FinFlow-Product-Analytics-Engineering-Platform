CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INT PRIMARY KEY,
    date        DATE,
    year        INT,
    quarter     INT,
    month       INT,
    month_name  VARCHAR,
    day         INT,
    week_of_year INT,
    day_of_week  INT,
    day_name     VARCHAR,
    is_weekend   BOOLEAN,
    is_month_start BOOLEAN,
    is_month_end   BOOLEAN
);

INSERT INTO dim_date
WITH dates AS (
    SELECT *
    FROM generate_series(
        MAKE_DATE(1945,01,01),
        CURRENT_DATE + INTERVAL '3 YEAR',
        INTERVAL '1 DAY'
    ) AS t(date)
)
SELECT
    CAST(strftime(date, '%Y%m%d') AS INTEGER) AS date_id,
    date,
    year(date),
    quarter(date),
    month(date),
    strftime(date, '%B'),
    day(date),
    week(date),
    dayofweek(date),
    strftime(date, '%A'),
    CASE WHEN dayofweek(date) IN (0,6) THEN TRUE ELSE FALSE END,
    CASE WHEN date = date_trunc('month', date) THEN TRUE ELSE FALSE END,
    CASE 
        WHEN date = (date_trunc('month', date) + INTERVAL 1 MONTH - INTERVAL 1 DAY)
        THEN TRUE ELSE FALSE
    END
FROM dates;