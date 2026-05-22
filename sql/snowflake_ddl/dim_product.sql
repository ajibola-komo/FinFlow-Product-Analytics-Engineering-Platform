CREATE OR REPLACE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_display_name VARCHAR(150) NOT NULL,
);