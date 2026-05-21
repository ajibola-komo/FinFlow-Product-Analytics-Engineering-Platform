import pandas as pd
import numpy as np
from src.config.constants import (DEFAULT_SIGNUP_START_DATE, DEFAULT_SIGNUP_END_DATE, DEFAULT_SIGNUP_START_TIMESTAMP, DEFAULT_SIGNUP_END_TIMESTAMP)
from datetime import timedelta

def get_signup_distribution(birth_dates_array):
    signup_dates = np.empty(len(birth_dates_array), dtype=pd.Timestamp)
    users_18 = pd.DateOffset(years=18)

    for i in range(len(birth_dates_array)):
        birth_date = birth_dates_array[i]
        min_signup_date = max(birth_date + users_18, pd.Timestamp(DEFAULT_SIGNUP_START_TIMESTAMP))
        max_signup_date = pd.Timestamp(DEFAULT_SIGNUP_END_TIMESTAMP)

        if min_signup_date > max_signup_date:
            signup_dates[i] = np.datetime64('NaT')
            continue
        else:
            date_range = (max_signup_date - min_signup_date).days
            random_offset = np.random.randint(0,int(date_range) + 1)
            signup_dates[i] = min_signup_date + timedelta(days=random_offset)

    return signup_dates