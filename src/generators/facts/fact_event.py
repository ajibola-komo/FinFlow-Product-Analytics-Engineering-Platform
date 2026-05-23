import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_EVENT_PATH, FACT_EVENTS_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP, DEFAULT_TRANSACTION_END_TIMESTAMP)


def generate_fact_events(conn, num_of_events):

    create_db = DDL_FACT_EVENT_PATH.read_text()

    conn.execute(create_db)

    