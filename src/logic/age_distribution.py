import numpy as np
from src.config.constants import (AGE_BUCKETS, AGE_WEIGHTS, )

def get_age_distribution(num_of_users):
    age_buckets = np.random.choice(AGE_BUCKETS, size=num_of_users, p=AGE_WEIGHTS)

    young_customers = np.where(age_buckets == '18-24')[0]
    adult_customers = np.where(age_buckets == '25-34')[0]
    middle_aged_customers = np.where(age_buckets == '35-44')[0]
    senior_customers = np.where(age_buckets == '45-54')[0]
    elderly_customers = np.where(age_buckets == '55-65')[0]

    age = np.empty(num_of_users, dtype=int)
    age[young_customers] = np.random.randint(18, 24, size=len(young_customers))
    age[adult_customers] = np.random.randint(25, 34, size=len(adult_customers))
    age[middle_aged_customers] = np.random.randint(35, 44, size=len(middle_aged_customers))
    age[senior_customers] = np.random.randint(45, 54, size=len(senior_customers))
    age[elderly_customers] = np.random.randint(55, 65, size=len(elderly_customers))

    return age