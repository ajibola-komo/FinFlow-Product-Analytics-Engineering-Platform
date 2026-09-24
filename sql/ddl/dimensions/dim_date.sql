CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INT PRIMARY KEY,
    full_date        DATE,
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
    SELECT
        date AS full_date
    FROM generate_series(
        MAKE_DATE(2016, 01, 01),
        CURRENT_DATE + INTERVAL '3 YEAR',
        INTERVAL '1 DAY'
    ) AS t(date)
)

SELECT
    CAST(strftime(full_date, '%Y%m%d') AS INTEGER) AS date_id,

    full_date,

    year(full_date) AS year,

    quarter(full_date) AS quarter,

    month(full_date) AS month,

    strftime(full_date, '%B') AS month_name,

    day(full_date) AS day,

    week(full_date) AS week_of_year,

    dayofweek(full_date) AS day_of_week,

    strftime(full_date, '%A') AS day_name,

    CASE
        WHEN dayofweek(full_date) IN (0, 6)
        THEN TRUE
        ELSE FALSE
    END AS is_weekend,

    CASE
        WHEN full_date = date_trunc('month', full_date)
        THEN TRUE
        ELSE FALSE
    END AS is_month_start,

    CASE
        WHEN full_date = (
            date_trunc('month', full_date)
            + INTERVAL '1 MONTH'
            - INTERVAL '1 DAY'
        )
        THEN TRUE
        ELSE FALSE
    END AS is_month_end

FROM dates;