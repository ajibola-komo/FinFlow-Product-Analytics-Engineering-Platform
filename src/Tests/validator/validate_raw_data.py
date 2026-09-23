import duckdb as db
import pandas as pd
import pandera as pa
from pandera.errors import *
from duckdb import DuckDBPyConnection
from Tests.contracts.dimensions.dim_date_schema import dim_date_schema
from Tests.contracts.dimensions.dim_user_schema import dim_user_schema
from Tests.contracts.dimensions.dim_wallet_schema import dim_wallet_schema
from Tests.contracts.facts.fact_investment_position_schema import fact_investment_position_schema
from Tests.contracts.facts.fact_transaction_schema import fact_transaction_schema
from Tests.contracts.facts.fact_user_event_schema import fact_user_event_schema
from Tests.contracts.facts.fact_wallet_balance_schema import fact_wallet_balance_schema
from src.config.paths import (DATES_PARQUET_PATH, USERS_PARQUET_PATH, WALLETS_PARQUET_PATH, FACT_WALLET_BALANCE_PARQUET_PATH, 
                              FACT_TRANSACTION_PARQUET_PATH, FACT_USER_EVENT_PARQUET_PATH, FACT_INVESTMENT_POSITION_PARQUET_PATH)


#create the df
def create_df_from_duckdb(conn:DuckDBPyConnection) -> dict:

    dim_user_df = conn.execute('''SELECT user_id, first_name, last_name, country, region, city, email_address, reported_annual_income, 
    acquisition_channel, device_type, customer_persona, kyc_completed, date_of_birth, birth_date_id,signup_date, signup_date_id,
     customer_behaviour_segment, last_login_at, created_at, last_updated_at FROM dim_user''').df()

    dim_wallet_df = conn.execute('''SELECT wallet_id, user_id, wallet_currency, wallet_created_at, wallet_activated_at, 
    wallet_created_date_id, wallet_activated_date_id, created_at, last_updated_at from dim_wallet''').df()

    dim_date_df = conn.execute('''SELECT date_id, full_date, year, quarter, month, month_name, day, week_of_year, day_of_week, day_name, is_weekend,
    is_month_start, is_month_end FROM dim_date''').df()

    fact_investment_position_df = conn.execute(''' SELECT investment_id, user_id, wallet_id, plan_id, amount_invested, expected_maturity_value,
    investment_start_date, investment_start_date_id, investment_maturity_date, investment_maturity_date_id, investment_status, is_withdrawn_early, penalty_amount,
    amount_paid_out, early_withdrawal_date, early_withdrawal_date_id, created_at, last_updated_at FROM fact_investment_position
''').df()

    fact_user_event_df = conn.execute(''' SELECT event_id, user_id, event_type_id, wallet_id, event_time, event_date_id, device_type, is_money_movement_activity, transaction_type_id,
    transaction_id, investment_id FROM fact_user_event
    ''').df()

    fact_transaction_df = conn.execute(''' SELECT transaction_id, wallet_id, transaction_type_id, transaction_amount, transaction_status, transaction_timestamp, transaction_date_id from fact_transaction
    ''').df()

    fact_wallet_balance_df = conn.execute(''' SELECT wallet_id, user_id, current_balance, last_updated_at, last_updated_date_id, last_transaction_id, created_at, updated_at 
    from fact_wallet_balance ''').df()

    extracted_dataframe_dictionary = {
        'dim_user':dim_user_df,
        'dim_wallet':dim_wallet_df,
        'dim_date':dim_date_df,
        'fact_investment_position':fact_investment_position_df,
        'fact_transaction':fact_transaction_df,
        'fact_user_event':fact_user_event_df,
        'fact_wallet_balance':fact_wallet_balance_df

    }

    return extracted_dataframe_dictionary


# validate df
def validate_data_frames(conn:DuckDBPyConnection):

    all_data_frames = create_df_from_duckdb(conn)

    dim_user_df = all_data_frames['dim_user']
    dim_wallet_df = all_data_frames['dim_wallet']
    dim_date_df = all_data_frames['dim_date']
    fact_investment_position_df = all_data_frames['fact_investment_position']
    fact_transaction_df = all_data_frames['fact_transaction']
    fact_user_event_df = all_data_frames['fact_user_event']
    fact_wallet_balance_df = all_data_frames['fact_wallet_balance']


    try:
        dim_user_df_validated = dim_user_schema.validate(dim_user_df,lazy=True)
    except SchemaError as e:
        print("dim_user validation failed")
        print(e)
        raise

    try:
        dim_wallet_df_validated = dim_wallet_schema.validate(dim_wallet_df,lazy=True)
    except SchemaError as e:
            print("dim_wallet validation failed")
            print(e)
            raise

    try:
        dim_date_df_validated = dim_date_schema.validate(dim_date_df,lazy=True)
    except SchemaError as e:
            print("dim_date validation failed")
            print(e)
            raise

    try:
        fact_investment_position_df_validated = fact_investment_position_schema.validate(fact_investment_position_df,lazy=True)
    except SchemaError as e:
            print("fact_investment_position validation failed")
            print(e)
            raise

    try:
        fact_transaction_df_validated = fact_transaction_schema.validate(fact_transaction_df,lazy=True)
    except SchemaError as e:
                print("fact_transaction validation failed")
                print(e)
                raise

    try:
        fact_user_event_df_validated = fact_user_event_schema.validate(fact_user_event_df,lazy=True)
    except SchemaError as e:
                print("fact_user_event validation failed")
                print(e)
                raise

    try:
        fact_wallet_balance_df_validated = fact_wallet_balance_schema.validate(fact_wallet_balance_df,lazy=True)
    except SchemaError as e:
                print("fact_wallet_balance validation failed")
                print(e)
                raise

    
    dim_user_df_validated.to_parquet(USERS_PARQUET_PATH, index=False)
    dim_date_df_validated.to_parquet(DATES_PARQUET_PATH, index=False)
    dim_wallet_df_validated.to_parquet(WALLETS_PARQUET_PATH, index=False)
    fact_user_event_df_validated.to_parquet(FACT_USER_EVENT_PARQUET_PATH,index=False)
    fact_investment_position_df_validated.to_parquet(FACT_INVESTMENT_POSITION_PARQUET_PATH,index=False)
    fact_wallet_balance_df_validated.to_parquet(FACT_WALLET_BALANCE_PARQUET_PATH, index=False)
    fact_transaction_df_validated.to_parquet(FACT_TRANSACTION_PARQUET_PATH,index=False)

    