CREATE OR REPLACE TABLE dim_plan (
    plan_id INT PRIMARY KEY,
    product_id INT NOT NULL,
    plan_name VARCHAR(50) NOT NULL,
    plan_display_name VARCHAR(50) NOT NULL,
    plan_category VARCHAR(50) NOT NULL,
    plan_weight decimal(5,2) NOT NULL,
    interest_rate_min DECIMAL(5,2) NOT NULL,
    interest_rate_max DECIMAL(5,2) NOT NULL,
    tenure_days INT,
    is_open_ended BOOLEAN NOT NULL,
    liquidity_type VARCHAR(50) NOT NULL,
    early_withdrawal_allowed BOOLEAN NOT NULL,
    penalty_rate_pct DECIMAL(5,2) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    foreign key (product_id) references dim_product(product_id)
)