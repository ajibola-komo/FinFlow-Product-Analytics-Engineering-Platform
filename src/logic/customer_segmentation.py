import numpy as np
import pandas as pd

def segment_customers(conn):

    starter_investors = conn.execute('''SELECT * FROM DIM_USER WHERE CUSTOMER_PERSONA = 'Starter Investor' ''').df()
    