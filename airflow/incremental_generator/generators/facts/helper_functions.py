import pandas as pd
from incremental_generator.config.constants import (GENERATION_START_DATE, INVESTMENT_WITHDRAWAL_PROCESSING_TIME)
import duckdb as db
from duckdb import DuckDBPyConnection


def update_last_login_timestamp(conn, user_ids, last_login):

    logins_df = pd.DataFrame({
        'user_id':user_ids,
        'last_login_at':last_login
    })

    conn.register('logins_df',logins_df)

    conn.execute('''
            UPDATE dim_user d set last_login_at = a.last_login_at from logins_df a where d.user_id = a.user_id
    ''')

    conn.unregister('logins_df')


def update_kyc_completion_status(conn, user_ids):

    kyc_df = pd.DataFrame({
        'user_id':user_ids,
        'kyc_status':True
    }
    )

    conn.register('kyc_df',kyc_df)

    conn.execute('''
            UPDATE dim_user d set kyc_completed = a.kyc_status from kyc_df a where d.user_id = a.user_id
    ''')

    conn.unregister('kyc_df')


def wallet_activation_funding(conn, user_ids, transaction_amounts, updated_at, transaction_ids, event_ids):

    df_current_wallet_updation = pd.DataFrame({
        'user_id': user_ids,
        'transaction_amount':transaction_amounts,
        'updated_at':updated_at,
        'transaction_ids':transaction_ids,
        'event_ids': event_ids
    })

    conn.register('wallet_updation', df_current_wallet_updation)

    conn.execute(f'''update dim_wallet d set wallet_activated_at = a.updated_at from wallet_updation a where d.user_id = a.user_id ''')
    conn.execute(f'''update fact_wallet_balance d set current_balance = (current_balance + a.transaction_amount),
    updated_at = a.updated_at, updated_at_id = CAST(STRFTIME(a.updated_at, '%Y%m%d') AS INTEGER), last_transaction_id = a.transaction_ids, last_event_id = a.event_ids 
                 from wallet_updation a where d.user_id = a.user_id ''')
        
    conn.unregister('wallet_updation')
        
    
def update_wallet_balance_topup(conn, user_ids, transaction_amounts, updated_at, transaction_ids, event_ids):

    df_current_wallet_updation = pd.DataFrame({
        'user_id': user_ids,
        'transaction_amount':transaction_amounts,
        'updated_at':updated_at,
        'transaction_ids':transaction_ids,
        'event_ids': event_ids
    })

    conn.register('wallet_updation', df_current_wallet_updation)

    conn.execute(f'''update fact_wallet_balance d set current_balance = (current_balance + a.transaction_amount),
                     updated_at = a.updated_at, updated_at_id = CAST(STRFTIME(a.updated_at, '%Y%m%d') AS INTEGER), last_transaction_id = a.transaction_ids,
                     last_event_id = a.event_ids
                     from wallet_updation a where d.user_id = a.user_id ''')
        
    conn.unregister('wallet_updation')
        
def debit_wallet_balance(conn, user_ids, transaction_amounts, updated_at, transaction_ids, event_ids):

    df_current_wallet_updation = pd.DataFrame({
        'user_id': user_ids,
        'transaction_amount':transaction_amounts,
        'updated_at':updated_at,
        'transaction_ids':transaction_ids,
        'event_ids': event_ids
    })

    conn.register('wallet_updation', df_current_wallet_updation)

    conn.execute(f'''update fact_wallet_balance d set current_balance = (current_balance - a.transaction_amount),
                     updated_at = a.updated_at, updated_at_id = CAST(STRFTIME(a.updated_at, '%Y%m%d') AS INTEGER), last_transaction_id = a.transaction_ids,
                     last_event_id = a.event_ids
                     from wallet_updation a where d.user_id = a.user_id ''')

    conn.unregister('wallet_updation')

def get_current_wallet_balance(conn, user_ids):

    conn.register('uids',user_ids)

    balances = conn.execute('''
                SELECT u.user_id, w.current_balance from fact_wallet_balance w inner join uids u on w.user_id = u.user_id
        ''').df()
    
    conn.unregister('uids')

    return balances

def early_withdrawal_requested_update(conn, investment_ids, request_timestamps):

    inv_ids = pd.DataFrame({
        'investment_id':investment_ids,
        'trans_time':request_timestamps
    })

    conn.register('inv_ids',inv_ids)

    conn.execute(F'''
                    update fact_investment_position f set is_withdrawn_early = True,
                 early_withdrawal_date = i.trans_time, early_withdrawal_date_id = CAST(strftime(i.trans_time::DATE,'%Y%m%d') as INTEGER)
                 from inv_ids i where f.investment_id = i.investment_id
    ''')

    conn.unregister('inv_ids')


def transfer_early_withdrawals_to_wallets(conn):

    eligible_investments = conn.execute('''
            SELECT * FROM FACT_INVESTMENT_POSITION WHERE is_withdrawn_early = True and investment_status = 'Active'
    ''').df()

    inv_df = pd.DataFrame({
        'investment_id':eligible_investments['investment_id'],
        'event_time':eligible_investments['early_withdrawal_date'] + pd.to_timedelta(INVESTMENT_WITHDRAWAL_PROCESSING_TIME,unit="M")
    })

    conn.register('inv_df',inv_df)

    conn.execute('''
        update fact_investment_position f set investment_status = 'Redeemed' from inv_df i where f.investment_id = i.investment_id
    ''')

    conn.unregister('inv_df')

    return inv_df


def update_early_withdrawal_requests_db(conn:DuckDBPyConnection, event_time:list[pd.Timestamp], early_withdrawal_df:pd.DataFrame) -> None:

    early_withdrawal_df = early_withdrawal_df.copy()

    early_withdrawal_df['withdrawal_request_date'] = event_time

    conn.register('early_withdrawal_df',early_withdrawal_df)

    conn.execute(f'''
                    UPDATE fact_investment_position f set early_withdrawal_date = e.withdrawal_request_date,
                    early_withdrawal_date_id = CAST(strftime(e.withdrawal_request_date::DATE, '%Y%m%d') AS INTEGER),
                    is_withdrawn_early = True,
                    investment_status = 'withdrawn_early',
                    last_updated_at = e.withdrawal_request_date
                    from early_withdrawal_df e
                    where f.investment_id = e.investment_id 
                ''')

    conn.unregister('early_withdrawal_df')

def update_investment_vests_db(conn:DuckDBPyConnection,matured_investments_df:pd.DataFrame) -> None:

    matured_investments_df = matured_investments_df.copy()

    conn.register('matured_investments_df',matured_investments_df)

    conn.execute('''
                    UPDATE fact_investment_position f set investment_status = 'matured',
                    last_updated_at = m.investment_maturity_date

                    from matured_investments_df m WHERE f.investment_id = m.investment_id
    ''')

    conn.unregister('matured_investments_df')

def update_asset_sale_events(conn:DuckDBPyConnection,assets_sale_df:pd.DataFrame) -> None:

    assets_sale_df = assets_sale_df.copy()

    