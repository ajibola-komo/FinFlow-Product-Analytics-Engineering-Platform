#this function generates the age and persona distributions for the list of users
import numpy as np
import pandas as pd
from src.config.constants import (CUSTOMER_PERSONAS, CUSTOMER_PERSONA_WEIGHTS,CUSTOMER_PERSONA_MAP, IS_ACTIVATED_USER)
from src.config.constants import (CURRENT_YEAR, CURRENT_MONTH)

def get_age_persona_income_distribution(num_of_users):
    customer_personas = np.random.choice(CUSTOMER_PERSONAS, size=num_of_users, p=CUSTOMER_PERSONA_WEIGHTS)

    min_age = [CUSTOMER_PERSONA_MAP[cp]['age_range'][0] for cp in customer_personas]
    max_age = [CUSTOMER_PERSONA_MAP[cp]['age_range'][1] for cp in customer_personas]

    min_income = [CUSTOMER_PERSONA_MAP[cp]['income_range'][0] for cp in customer_personas]
    max_income = [CUSTOMER_PERSONA_MAP[cp]['income_range'][1] for cp in customer_personas]

    is_activated_user = np.array([np.random.choice(IS_ACTIVATED_USER, p=CUSTOMER_PERSONA_MAP[cp]['wallet_activation_weight']) for cp in customer_personas])

    
    age = [np.random.randint(min_a, max_a) for min_a, max_a in zip(min_age,max_age)]
    income = [np.random.randint(min_i,max_i) for min_i, max_i in zip(min_income, max_income)]

    birth_year = [CURRENT_YEAR - age[i] for i in range(num_of_users)]

    birth_date = np.array([
    pd.Timestamp(
        year=int(birth_year[i]),
        month=np.random.randint(1, CURRENT_MONTH if birth_year[i] == CURRENT_YEAR - 18 else 13),
        day=np.random.randint(1, 29)
    )
    for i in range(num_of_users)], dtype='datetime64[ns]')

    min_mins = np.array([CUSTOMER_PERSONA_MAP[cp]['mins_to_first_funding'][0] for cp in customer_personas])
    max_mins = np.array([CUSTOMER_PERSONA_MAP[cp]['mins_to_first_funding'][1] for cp in customer_personas])

    random_offset_for_wallet_activation = np.full(num_of_users, np.nan) #initialize with NaN, will fill only for activated users

    activated_indices = np.where(is_activated_user == True)[0]

    random_offset_for_wallet_activation[activated_indices] = [np.random.randint(min_m,max_m) for min_m,max_m in zip(min_mins[activated_indices], max_mins[activated_indices])]

    return pd.DataFrame({
        'birth_date':birth_date,
        'persona':customer_personas,
        'income':income,
        'is_activated_user':is_activated_user,
        'wallet_activation_timeframe':random_offset_for_wallet_activation
        })