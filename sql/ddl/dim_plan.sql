CREATE OR REPLACE TABLE dim_plan (
    plan_id INTEGER PRIMARY KEY,

    product_id INTEGER,

    plan_name VARCHAR(50),
    plan_display_name VARCHAR(50),

    plan_category VARCHAR(50),

    interest_rate_min DECIMAL(5,2),
    interest_rate_max DECIMAL(5,2),

    tenure_days INTEGER,

    is_open_ended BOOLEAN,

    liquidity_type VARCHAR(50),

    early_withdrawal_allowed BOOLEAN,

    penalty_rate_pct DECIMAL(5,2),

    risk_level VARCHAR(50)
);