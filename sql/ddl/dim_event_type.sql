CREATE TABLE dim_event_type (
    event_type_id INT PRIMARY KEY,
    event_type_code VARCHAR(100) NOT NULL,
    event_type_display_name VARCHAR(150) NOT NULL,
    event_type_description VARCHAR(255) NOT NULL,
    event_type_category VARCHAR(50) NOT NULL,
    event_type_stage VARCHAR(50) NOT NULL,
    is_conversion_milestone BOOLEAN NOT NULL,
    product_area VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);