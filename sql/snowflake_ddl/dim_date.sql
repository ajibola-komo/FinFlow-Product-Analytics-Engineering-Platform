CREATE OR REPLACE TABLE dim_date (
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
WITH params AS (
    SELECT 
        DATE '2023-01-01' AS start_date,
        DATEADD(YEAR, 3, CURRENT_DATE()) AS end_date,
        DATEDIFF(
            DAY,
            DATE '2023-01-01',
            DATEADD(YEAR, 3, CURRENT_DATE())
        ) AS day_count
),
dates AS (
    SELECT 
        DATEADD(DAY, SEQ4(), (SELECT start_date FROM params)) AS date
    FROM TABLE(GENERATOR(ROWCOUNT => (SELECT day_count FROM params)))
)
SELECT
    TO_NUMBER(TO_CHAR(date, 'YYYYMMDD')) AS date_id,
    date,

    YEAR(date) AS year,
    QUARTER(date) AS quarter,
    MONTH(date) AS month,

    TRIM(TO_CHAR(date, 'Month')) AS month_name,

    DAY(date) AS day,

    WEEKOFYEAR(date) AS week_of_year,

    DAYOFWEEK(date) AS day_of_week,

    TRIM(TO_CHAR(date, 'Day')) AS day_name,

    CASE 
        WHEN DAYOFWEEK(date) BETWEEN 1 AND 5 THEN TRUE 
        ELSE FALSE 
    END AS is_weekday,

    CASE 
        WHEN DAYOFWEEK(date) IN (0,6) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend,

    CASE 
        WHEN date = DATE_TRUNC('MONTH', date) THEN TRUE 
        ELSE FALSE 
    END AS is_month_start,

    CASE 
        WHEN date = DATEADD(DAY, -1, DATEADD(MONTH, 1, DATE_TRUNC('MONTH', date)))
        THEN TRUE 
        ELSE FALSE 
    END AS is_month_end

FROM dates;