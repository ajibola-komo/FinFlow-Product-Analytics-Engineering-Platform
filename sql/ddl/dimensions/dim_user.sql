CREATE OR REPLACE TABLE dim_user(
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    country VARCHAR(50),
    region VARCHAR(50),
    city VARCHAR(50),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    kyc_completed BOOLEAN NOT NULL,
    date_of_birth DATE,
    birth_date_id INT,
    signup_date DATE NOT NULL,
    signup_date_id INT,
    foreign key (birth_date_id) references dim_date(date_id),
    foreign key (signup_date_id) references dim_date(date_id)
)