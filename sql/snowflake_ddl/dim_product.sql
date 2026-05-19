CREATE OR REPLACE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_display_name VARCHAR(150) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    interest_rate_min INT,
    interest_rate_max INT,
    tenure_days INT,
    is_open_ended BOOLEAN NOT NULL,
    liquidity_type VARCHAR(50) NOT NULL,
    early_withdrawal_allowed BOOLEAN NOT NULL,
    penalty_rate_pct DECIMAL(5,2),
    risk_level VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);