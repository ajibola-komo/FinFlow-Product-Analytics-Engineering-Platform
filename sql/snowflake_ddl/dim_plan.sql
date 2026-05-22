CREATE OR REPLACE TABLE dim_plan (
    plan_id INTEGER PRIMARY KEY,

    product_id INTEGER,

    plan_name VARCHAR,
    plan_display_name VARCHAR,

    plan_category VARCHAR,

    interest_rate_min DECIMAL(5,2),
    interest_rate_max DECIMAL(5,2),

    tenure_days INTEGER,

    is_open_ended BOOLEAN,

    liquidity_type VARCHAR,

    early_withdrawal_allowed BOOLEAN,

    penalty_rate_pct DECIMAL(5,2),

    risk_level VARCHAR
);