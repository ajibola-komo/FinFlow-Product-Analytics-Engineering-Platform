import numpy as np
import pandas as pd
import faker as fk
import re
from src.config.constants import (DEFAULT_SIGNUP_START_DATE, DEFAULT_SIGNUP_END_DATE, DEFAULT_SIGNUP_START_TIMESTAMP, 
                                  DEFAULT_SIGNUP_END_TIMESTAMP, EMAIL_DOMAIN, GENDER, GENDER_WEIGHTS, 
                                  )
from src.config.paths import (DDL_DIM_USER_PATH, USERS_PARQUET_PATH)
from src.logic.location_distribution import get_location_distribution
from src.logic.age_distribution import get_age_distribution
from src.logic.signup_distribution import get_signup_distribution


def generate_users(conn, num_of_users):
    #read the DDL SQL file and execute it to create the dim_user table
    create_db = DDL_DIM_USER_PATH.read_text()

    conn.execute(create_db)

    #generate fake user data using faker library
    fake_gb = fk.Faker('en_GB')
    fake_ie = fk.Faker('en_IE')

    #user_id = np.arange(1, num_of_users + 1)
    gender = np.random.choice(GENDER, num_of_users, p=GENDER_WEIGHTS)
    customer_first_names = np.empty(num_of_users, dtype=object)
    customer_last_names = np.empty(num_of_users, dtype=object)

    location_data = get_location_distribution(num_of_users)
    regions = location_data['regions']
    cities = location_data['cities']
    countries = location_data['countries']
    
    uk_male_customers = np.where((gender == 'Male') & (countries == 'UK'))[0]
    uk_female_customers = np.where((gender == 'Female') & (countries == 'UK'))[0]
    uk_other_customers = np.where((gender == 'Other') & (countries == 'UK'))[0]
    ie_male_customers = np.where((gender == 'Male') & (countries == 'Ireland'))[0]
    ie_female_customers = np.where((gender == 'Female') & (countries == 'Ireland'))[0]
    ie_other_customers = np.where((gender == 'Other') & (countries == 'Ireland'))[0]

    #male names assignment based on nationality
    customer_first_names[uk_male_customers] = [fake_gb.first_name_male() for _ in range(len(uk_male_customers))]
    customer_last_names[uk_male_customers] = [fake_gb.last_name_male() for _ in range(len(uk_male_customers))]
    customer_first_names[ie_male_customers] = [fake_ie.first_name_male() for _ in range(len(ie_male_customers))]
    customer_last_names[ie_male_customers] = [fake_ie.last_name_male() for _ in range(len(ie_male_customers))]

    #female names assignment based on nationality
    customer_first_names[uk_female_customers] = [fake_gb.first_name_female() for _ in range(len(uk_female_customers))]
    customer_last_names[uk_female_customers] = [fake_gb.last_name_female() for _ in range(len(uk_female_customers))]
    customer_first_names[ie_female_customers] = [fake_ie.first_name_female() for _ in range(len(ie_female_customers))]
    customer_last_names[ie_female_customers] = [fake_ie.last_name_female() for _ in range(len(ie_female_customers))]

    #other names assignment based on nationality
    customer_first_names[uk_other_customers] = [fake_gb.first_name_nonbinary() for _ in range(len(uk_other_customers))]
    customer_last_names[uk_other_customers] = [fake_gb.last_name_nonbinary() for _ in range(len(uk_other_customers))]
    customer_first_names[ie_other_customers] = [fake_ie.first_name_nonbinary() for _ in range(len(ie_other_customers))]
    customer_last_names[ie_other_customers] = [fake_ie.last_name_nonbinary() for _ in range(len(ie_other_customers))]


    first_name = np.array([re.sub(r'[^a-z]', '', name.lower())
                                for name in customer_first_names])
    last_name = np.array([re.sub(r'[^a-z]', '', name.lower())
                               for name in customer_last_names])
    email_ids = np.empty(num_of_users, dtype=object)
    email_domains = np.random.choice(EMAIL_DOMAIN, num_of_users)
    random_suffix = np.arange(
    1,
    num_of_users + 1
)
    email_ids = [f"{first_name[i].lower()}.{last_name[i].lower()}{random_suffix[i]}{email_domains[i]}" for i in range(num_of_users)]


    kyc_completed = np.random.choice([True, False], num_of_users, p=[0.7, 0.3])
    date_of_birth = get_age_distribution(num_of_users)
    signup_date = get_signup_distribution(date_of_birth)
    birth_date_id = [int(pd.Timestamp(date_of_birth[i]).strftime('%Y%m%d')) for i in range(num_of_users)]
    signup_date_id = [int(pd.Timestamp(signup_date[i]).strftime('%Y%m%d')) for i in range(num_of_users)]

    df_raw = pd.DataFrame({
        'first_name': customer_first_names,
        'last_name': customer_last_names,
        'country': countries,
        'region': regions,
        'city': cities,
        'email_address': email_ids,
        'kyc_completed': kyc_completed,
        'date_of_birth': date_of_birth,
        'birth_date_id': birth_date_id,
        'signup_date': signup_date,
        'signup_date_id': signup_date_id
    })

    df_raw = df_raw.sort_values(
    by='signup_date'
    ).reset_index(drop=True)

    df_raw['user_id'] = np.arange(
    1,
    len(df_raw) + 1
    )

    df_raw = df_raw[[
    'user_id',
    'first_name',
    'last_name',
    'country',
    'region',
    'city',
    'email_address',
    'kyc_completed',
    'date_of_birth',
    'birth_date_id',
    'signup_date',
    'signup_date_id'
]]

    #write the generated data to a parquet file
    conn.register('df_raw', df_raw)
    conn.execute('''INSERT INTO dim_user SELECT * FROM df_raw''')

    conn.execute(f'''COPY DIM_USER TO '{USERS_PARQUET_PATH}' (FORMAT PARQUET) ''')

