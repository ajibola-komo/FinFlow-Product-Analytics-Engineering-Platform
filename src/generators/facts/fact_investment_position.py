import pandas as pd
import numpy as np
from src.config.paths import (DDL_FACT_INVESTMENT_POSITION_PATH, FACT_INVESTMENT_POSITION_PARQUET_PATH)

def generate_historical_investments(num_of_positions, conn):

    create_db = DDL_FACT_INVESTMENT_POSITION_PATH.read_text()

    conn.execute(create_db)

    #investment_id (PK)
    #user_id
    #plan_id
    #amount_invested
    #investment_start_date
    #investment_start_date_id
    #investment_maturity_date
    #investment_maturity_date_id
    #investment_status
    #wallet_id
    #transaction_id

    high_engagement_high_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    
    ''').df()

    high_engagement_low_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    
    ''').df()

    moderate_engagement_high_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    
    ''').df()

    moderate_engagement_low_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    
    ''').df()


    low_engagement_low_balance_users = moderate_engagement_high_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    ''').df()

    low_engagement_high_balance_users = conn.execute('''
            SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = '' or CUSTOMER_PERSONA = ''
    ''').df()


