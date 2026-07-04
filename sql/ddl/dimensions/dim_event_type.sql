CREATE OR REPLACE TABLE dim_event_type (
    event_type_id INT PRIMARY KEY,
    event_type_code VARCHAR(100),
    event_type_display_name VARCHAR(150),
    event_type_description VARCHAR(255),
    event_type_category VARCHAR(50),
    event_type_stage VARCHAR(50),
    is_conversion_milestone BOOLEAN,
    product_area VARCHAR(50)
);