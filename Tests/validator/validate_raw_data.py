import duckdb as db
import pandas as pd
import pandera as pa
from duckdb import DuckDBPyConnection



def create_df(conn:DuckDBPyConnection):

    dim_user_df = conn.execute('''SELECT user_id, first_name, last_name, country, region, city, email_address, reported_annual_income, 
    acquisition_channel, device_type, customer_persona, kyc_completed, date_of_birth, birth_date_id,signup_date, signup_date_id,
     customer_behaviour_segment, last_login_at, created_at, last_updated_at FROM dim_user''').df()

    dim_wallet_df = conn.execute('''SELECT wallet_id, user_id, wallet_currency, wallet_created_at, wallet_activated_at, 
    wallet_created_date_id, wallet_activated_date_id, created_at, last_updated_at from dim_wallet''').df()

    dim_date_df = conn.execute('''SELECT date_id, full_date, year, quarter, month, month_name, day, week_of_year, day_of_week, day_name, is_weekend,
    is_month_start, is_month_end''').df()

    fact_investment_position_df = conn.execute().df()

    