CREATE OR REPLACE TABLE dim_transaction_type(
    transaction_type_id INT,
    transaction_type_code VARCHAR(50),
    transaction_type_name VARCHAR(50),
    transaction_type_description VARCHAR(255),
    transaction_category VARCHAR(50),
    transaction_direction VARCHAR(10)
);