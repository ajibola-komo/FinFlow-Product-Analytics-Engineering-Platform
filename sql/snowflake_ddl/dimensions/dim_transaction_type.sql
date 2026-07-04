CREATE OR REPLACE TABLE dim_transaction_type(
    transaction_type_id INT PRIMARY KEY,
    transaction_type_code VARCHAR(50) NOT NULL,
    transaction_type_name VARCHAR(50) NOT NULL,
    transaction_type_description VARCHAR(255) NOT NULL,
    transaction_category VARCHAR(50) NOT NULL,
    transaction_direction VARCHAR(10) NOT NULL
);