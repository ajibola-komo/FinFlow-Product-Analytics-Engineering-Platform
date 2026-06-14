CREATE OR REPLACE TABLE FINFLOW.BRONZE.DIM_DATE (
    date_id BIGINT,
    full_date DATE,
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
);