CREATE OR REPLACE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR,
    day INT,
    week_of_year INT,
    day_of_week INT,
    day_name VARCHAR,
    is_weekend BOOLEAN,
    is_month_start BOOLEAN,
    is_month_end BOOLEAN
)