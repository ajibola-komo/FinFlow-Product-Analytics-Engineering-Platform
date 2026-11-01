import pandas as pd
from incremental_generator.config.constants import (GENERATION_START_DATE, INVESTMENT_WITHDRAWAL_PROCESSING_TIME)
import duckdb as db
import numpy as np
from duckdb import DuckDBPyConnection
from src.logic.helper_functions import (review_current_investment_events, update_wallet_balance)


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
        update fact_investment_position f set investment_status = 'redeemed' from inv_df i where f.investment_id = i.investment_id
    ''')

    conn.unregister('inv_df')

    return inv_df

def update_early_withdrawal_requests_db(conn:DuckDBPyConnection, early_withdrawal_df:pd.DataFrame) -> None:

    early_withdrawal_df = early_withdrawal_df.copy()

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

def update_asset_sale_events(conn:DuckDBPyConnection,event_time:list[pd.Timestamp],assets_sale_df:pd.DataFrame) -> None:

    assets_sale_df = assets_sale_df.copy()

    assets_sale_df['withdrawal_request_date'] = event_time

    conn.register('assets_sale_df',assets_sale_df)

    conn.execute('''
                    UPDATE fact_investment_position f set investment_status = 'sale_processing', redemption_request_date = a.withdrawal_request_date
                    FROM assets_sale_df a where f.investment_id = a.investment_id
    
    ''')

    conn.unregister('assets_sale_df')

def request_early_withdrawal_events(conn:DuckDBPyConnection,context:any, start_position:int, end_position:int, user_ids:list[int],event_times:list[pd.Timestamp],
                                    event_type_ids:list[int],investment_ids:list[int],device_types:list[str],dtypes,early_withdrawal_requests_df:pd.DataFrame) -> int :



        early_withdrawal_requests_df = early_withdrawal_requests_df.copy()
        
        
        early_withdrawal_requests_df['investment_start_date'] = pd.to_datetime(early_withdrawal_requests_df['investment_start_date'])
        
        early_withdrawal_requests_df['review_current_investment_time'] = [rd - pd.to_timedelta((np.random.randint(3,9)),unit='m') for rd in early_withdrawal_requests_df['withdrawal_request_date']]

        early_withdrawal_requests_df['days_held'] = (pd.to_datetime(GENERATION_START_DATE) - early_withdrawal_requests_df['investment_start_date']).dt.days
        
        
        updated_end_position = review_current_investment_events(conn, context, start_position, end_position, user_ids, early_withdrawal_requests_df['user_id'], event_times, early_withdrawal_requests_df['review_current_investment_time'],
                                             device_types, dtypes, event_type_ids)
        
        
            #request withdrawal
        start_position = updated_end_position
        end_position = start_position + len(early_withdrawal_requests_df)
        
        user_ids[start_position:end_position] = early_withdrawal_requests_df['user_id']
        event_times[start_position:end_position] = early_withdrawal_requests_df['withdrawal_request_date']
        investment_ids[start_position:end_position] = early_withdrawal_requests_df['investment_id']
        event_type_ids[start_position:end_position] = [context.request_early_withdrawal_event_type_id] * len(early_withdrawal_requests_df)
        device_types[start_position:end_position] = dtypes

        updated_end_position = end_position

        update_early_withdrawal_requests_db(conn, early_withdrawal_requests_df)

        return updated_end_position
    
def incremental_early_withdrawal_investments_proceeds_transfer(conn:DuckDBPyConnection,context:any, start_position:int, end_position:int, user_ids:list[int], wallet_ids:list[int], 
                                     is_money_movement_activity:list[bool], last_transaction_id:int, event_times:list[pd.Timestamp], device_types:list[str], dtypes:list[str], 
                                     pending_early_withdrawal_requests_df:pd.DataFrame, event_type_ids:list[int], transaction_types_ids:list[int],transaction_ids:list[int], 
                                     transaction_amounts:list[float], transaction_statuses:list[str], investment_ids:list[int]) -> dict:

    if pending_early_withdrawal_requests_df.empty:
        return{
            'last_transaction_id':last_transaction_id,
            'updated_end_position':end_position
        }

    pending_early_withdrawal_requests_df = pending_early_withdrawal_requests_df.copy()

    #investment_proceeds_wallet_transfer
    start_position = end_position
    end_position = start_position + len(pending_early_withdrawal_requests_df)

    user_ids[start_position:end_position] = pending_early_withdrawal_requests_df['user_id']
    investment_ids[start_position:end_position] = pending_early_withdrawal_requests_df['investment_id']
    event_times[start_position:end_position] = pending_early_withdrawal_requests_df['early_withdrawal_date'] + pd.to_timedelta(INVESTMENT_WITHDRAWAL_PROCESSING_TIME,unit='m')
    is_money_movement_activity[start_position:end_position] = [True] * len(pending_early_withdrawal_requests_df)
    event_type_ids[start_position:end_position] = [context.investment_proceeds_wallet_transfer_event_type_id] * len(pending_early_withdrawal_requests_df)
    transaction_types_ids[start_position:end_position] = [context.investment_proceeds_transfer_transaction_type_id] * len(pending_early_withdrawal_requests_df)
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id + 1 + len(pending_early_withdrawal_requests_df))    
    device_types[start_position:end_position] = dtypes
    last_transaction_id = transaction_ids[start_position:end_position].max()
    wallet_ids[start_position:end_position] = pending_early_withdrawal_requests_df['wallet_id']
    pending_early_withdrawal_requests_df['days_held'] = (pd.to_datetime(pending_early_withdrawal_requests_df['early_withdrawal_date']) - pd.to_datetime(pending_early_withdrawal_requests_df['investment_start_date'])).dt.days
    pending_early_withdrawal_requests_df['tenure_days'] = (pd.to_datetime(pending_early_withdrawal_requests_df['investment_maturity_date']) - pd.to_datetime(pending_early_withdrawal_requests_df['investment_start_date'])).dt.days
    
    pending_early_withdrawal_requests_df['expected_total_interest'] = pending_early_withdrawal_requests_df['expected_maturity_value'] - pending_early_withdrawal_requests_df['amount_invested']
    pending_early_withdrawal_requests_df['interest_accrued'] = pending_early_withdrawal_requests_df['expected_total_interest'] * (pending_early_withdrawal_requests_df['days_held'] / pending_early_withdrawal_requests_df['tenure_days'])
    pending_early_withdrawal_requests_df['penalty_amount'] = (pending_early_withdrawal_requests_df['interest_accrued']  * (pending_early_withdrawal_requests_df['penalty_rate_pct'] / 100))

    transaction_amounts[start_position:end_position] = ((pending_early_withdrawal_requests_df['amount_invested'] + pending_early_withdrawal_requests_df['interest_accrued'])  - pending_early_withdrawal_requests_df['penalty_amount'])
    pending_early_withdrawal_requests_df['investment_status'] = "redeemed"
    transaction_statuses[start_position:end_position] = ["Success"] * len(pending_early_withdrawal_requests_df)
    pending_early_withdrawal_requests_df['amount_paid_out'] = ((pending_early_withdrawal_requests_df['amount_invested'] + pending_early_withdrawal_requests_df['interest_accrued'])  - pending_early_withdrawal_requests_df['penalty_amount'])
    pending_early_withdrawal_requests_df['last_updated_at'] = event_times[start_position:end_position]

    updated_end_position= end_position

    update_wallet_balance(conn, pending_early_withdrawal_requests_df['user_id'], pending_early_withdrawal_requests_df['amount_paid_out'],
                          transaction_ids[start_position:end_position],event_times[start_position:end_position])


    conn.register('pending_transactions',pending_early_withdrawal_requests_df)

    conn.execute('''
                    UPDATE FACT_INVESTMENT_POSITION f set investment_status = 'redeemed', penalty_amount = p.penalty_amount, amount_paid_out = p.amount_paid_out, last_updated_at = p.last_updated_at
                    FROM pending_transactions p WHERE f.investment_id = p.investment_id and investment_status = 'withdrawn_early'
    ''')

    conn.unregister('pending_transactions')

    return {
        'last_transaction_id':last_transaction_id,
        'updated_end_position':updated_end_position
    }

def update_new_investments(conn:DuckDBPyConnection, new_investments_df:pd.DataFrame) -> None :

    new_investments_df = new_investments_df.copy()

    new_investments_df = new_investments_df.drop(columns=['tenure_days'])

    conn.register('new_investments_df',new_investments_df)

    conn.execute('''
                    INSERT INTO fact_investment_position SELECT * FROM NEW_INVESTMENTS_DF
                ''')

    conn.unregister('new_investments_df')

def incremental_vested_investment_events(conn:DuckDBPyConnection, context:any, start_position:int, end_position:int, user_ids:list[int],
                                         event_time:list[pd.Timestamp],event_type_ids:list[int],investment_ids:list[int],
                                         device_types:list[str],dtypes:list[str],vested_investments_df:pd.DataFrame):

     vested_investments_df = vested_investments_df.copy()

     user_ids[start_position:end_position] = vested_investments_df['user_id']
     event_type_ids[start_position:end_position] = [context.investment_vests_event_type_id] * len(vested_investments_df)
     event_time[start_position:end_position] = vested_investments_df['investment_maturity_date']
     device_types[start_position:end_position] = dtypes
     investment_ids[start_position:end_position] = vested_investments_df['investment_id']

     conn.register('vested_investments_df',vested_investments_df)

     conn.execute('''
            UPDATE FACT_INVESTMENT_POSITION as f set investment_status = 'Matured', last_updated_at = v.investment_maturity_date
            FROM vested_investments_df as v WHERE f.investment_id = v.investment_id
    ''')

     conn.unregister('vested_investments_df')

def incremental_vested_investments_proceeds_transfer_events(conn:DuckDBPyConnection, context:any, start_position:int, end_position:int, user_ids:list[int], event_time:list[pd.Timestamp], 
                                                wallet_ids:list[int], last_transaction_id:int,is_money_movement_activity:list[bool],transaction_type_ids:list[int], transaction_ids:list[int], 
                                                transaction_amounts:list[float], transaction_statuses:list[str],
                                                event_type_ids:list[int], device_types:list[str], dtypes:list[str], investment_ids:list[int],
                                                matured_investment_df:pd.DataFrame) -> int:


    if matured_investment_df.empty:
        return {
        'last_transaction_id': last_transaction_id
    }

    user_ids[start_position:end_position] = matured_investment_df['user_id']
    wallet_ids[start_position:end_position] = matured_investment_df['user_id']
    investment_ids[start_position:end_position] = matured_investment_df['investment_id']
    is_money_movement_activity[start_position:end_position] = [True] * len(matured_investment_df)
    event_type_ids[start_position:end_position] = [context.investment_proceeds_wallet_transfer_event_type_id] * len(matured_investment_df)
    device_types[start_position:end_position] = dtypes
    transaction_type_ids[start_position:end_position] = [context.investment_proceeds_transfer_transaction_type_id] * len(matured_investment_df)
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id + 1 + len(matured_investment_df))
    transaction_amounts[start_position:end_position] = matured_investment_df['expected_maturity_value']
    transaction_statuses[start_position:end_position] = ["Success"] * len(matured_investment_df)
    event_time[start_position:end_position] = matured_investment_df['investment_maturity_date'] + pd.to_timedelta(INVESTMENT_WITHDRAWAL_PROCESSING_TIME,unit='m')
    matured_investment_df['last_updated_at'] = event_time[start_position:end_position]
    matured_investment_df['amount_paid_out'] = matured_investment_df['expected_maturity_value']
    

    conn.register('matured_investment_df',matured_investment_df)

    conn.execute(f'''
                    UPDATE fact_investment_position as f set investment_status = 'redeemed', amount_paid_out = m.expected_maturity_value, is_withdrawn_early = False,
                    early_withdrawal_date = NULL, early_withdrawal_date_id = NULL, last_updated_at = m.last_updated_at FROM matured_investment_df as m
                    WHERE f.investment_id = m.investment_id and investment_status = 'matured'
    ''')

    conn.unregister('vested_investment_df')

    last_transaction_id = transaction_ids[start_position:end_position].max()

    update_wallet_balance(conn,matured_investment_df['user_id'], matured_investment_df['amount_paid_out'],
                          transaction_ids[start_position:end_position],event_time[start_position:end_position]  )

    return last_transaction_id

def upload_newly_created_investments_to_db(conn:DuckDBPyConnection, new_investments_df:pd.DataFrame) -> None :

    new_investments_df = new_investments_df.copy()

    conn.register('new_investments_df', new_investments_df)

    try:
        conn.execute("""
        INSERT INTO FACT_INVESTMENT_POSITION (
            investment_id,
            user_id,
            wallet_id,
            plan_id,
            amount_invested,
            expected_maturity_value,
            investment_start_date,
            investment_start_date_id,
            investment_maturity_date,
            investment_maturity_date_id,
            investment_status,
            is_withdrawn_early,
            penalty_amount,
            amount_paid_out,
            early_withdrawal_date,
            early_withdrawal_date_id,
            created_at,
            last_updated_at
        )
        SELECT
            investment_id,
            user_id,
            wallet_id,
            plan_id,
            amount_invested,
            expected_maturity_value,
            investment_start_date,
            investment_start_date_id,
            investment_maturity_date,
            investment_maturity_date_id,
            investment_status,
            is_withdrawn_early,
            penalty_amount,
            amount_paid_out,
            early_withdrawal_date,
            early_withdrawal_date_id,
            created_at,
            last_updated_at
        FROM new_investments_df
    """)
    finally:
        conn.unregister('new_investments_df')
    
def incremental_assets_sale_investment_proceeds_wallet_transfer_events(conn:DuckDBPyConnection, context:any, start_position:int, end_position:int, user_ids:list[int], wallet_ids:list[int],
                                                    event_time:list[pd.Timestamp], device_types:list[str], dtypes, transaction_type_ids:list[int], transaction_ids:list[int],
                                                    last_transaction_id:int, event_type_ids, is_money_movement_activity:list[bool], transaction_amounts:list[float], transaction_statuses:list[str],
                                                    investment_ids:list[int],
                                                    saleable_investment_df:pd.DataFrame) -> int:


    ''''
    This function creates the investment proceeds wallet transfer events for the saleable investments.
    It returns the last transaction id after creating the events.
    '''

    if saleable_investment_df.empty:
        return last_transaction_id

    saleable_investment_df = saleable_investment_df.copy()

    user_ids[start_position:end_position] = saleable_investment_df['user_id']
    event_time[start_position:end_position] = (saleable_investment_df['redemption_request_date'] + pd.to_timedelta(INVESTMENT_WITHDRAWAL_PROCESSING_TIME, unit='m'))
    is_money_movement_activity[start_position:end_position] = [True] * len(saleable_investment_df)
    device_types[start_position:end_position] = dtypes
    investment_ids[start_position:end_position] = saleable_investment_df['investment_id']
    event_type_ids[start_position:end_position] = [context.investment_proceeds_wallet_transfer_event_type_id] * len(saleable_investment_df)
    transaction_type_ids[start_position:end_position] = [context.investment_proceeds_transfer_transaction_type_id] * len(saleable_investment_df)
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id + 1 + len(saleable_investment_df))
    last_transaction_id = transaction_ids[start_position:end_position].max()
    wallet_ids[start_position:end_position] = saleable_investment_df['user_id']

    #get interest rate
    saleable_investment_df['interest_rate'] = np.random.randint(8,19,size=len(saleable_investment_df))
    saleable_investment_df['amount_paid_out'] = (saleable_investment_df['amount_invested'] * (1 + (saleable_investment_df['interest_rate']/100))).round(2)
    transaction_amounts[start_position:end_position] = saleable_investment_df['amount_paid_out']
    transaction_statuses[start_position:end_position] = ["success"] * len(saleable_investment_df)
    saleable_investment_df['investment_status'] = ["redeemed"] * len(saleable_investment_df)
    saleable_investment_df['is_withdrawn_early'] = False
    saleable_investment_df['penalty_amount'] = 0.0
    saleable_investment_df['early_withdrawal_date'] = None
    saleable_investment_df['early_withdrawal_date_id'] = None
    saleable_investment_df['last_updated_at'] = event_time[start_position:end_position]

    update_wallet_balance(conn, saleable_investment_df['user_id'], transaction_amounts[start_position:end_position], transaction_ids[start_position:end_position], event_time[start_position:end_position])

    conn.register('saleable_investment_df', saleable_investment_df)

    conn.execute('''
                    UPDATE FACT_INVESTMENT_POSITION f SET investment_status = 'redeemed', 
                    is_withdrawn_early = FALSE, 
                    penalty_amount = 0.0, 
                    amount_paid_out = s.amount_paid_out, early_withdrawal_date = NULL, early_withdrawal_date_id = NULL, last_updated_at = s.last_updated_at
                    FROM saleable_investment_df s WHERE f.investment_id = s.investment_id and f.investment_status = 'sale_processing'
    ''')

    conn.unregister('saleable_investment_df')

    return last_transaction_id

