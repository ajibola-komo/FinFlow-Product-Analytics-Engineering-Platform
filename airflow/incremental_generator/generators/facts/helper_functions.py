import pandas as pd


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
    
