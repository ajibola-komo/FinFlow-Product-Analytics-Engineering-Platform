#this function generates the age and persona distributions for the list of users
import numpy as np
import pandas as pd
from src.config.constants import (CUSTOMER_PERSONAS, CUSTOMER_PERSONA_WEIGHTS,CUSTOMER_PERSONA_MAP)
from src.config.constants import (CURRENT_YEAR, CURRENT_MONTH)

def get_age_persona_income_distribution(num_of_users):
    customer_personas = np.random.choice(CUSTOMER_PERSONAS, size=num_of_users, p=CUSTOMER_PERSONA_WEIGHTS)

    min_age = [CUSTOMER_PERSONA_MAP[cp]['age_range'][0] for cp in customer_personas]
    max_age = [CUSTOMER_PERSONA_MAP[cp]['age_range'][1] for cp in customer_personas]

    min_income = [CUSTOMER_PERSONA_MAP[cp]['income_range'][0] for cp in customer_personas]
    max_income = [CUSTOMER_PERSONA_MAP[cp]['income_range'][1] for cp in customer_personas]

    
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

    return pd.DataFrame({
        'birth_date':birth_date,
        'persona':customer_personas,
        'income':income
        })