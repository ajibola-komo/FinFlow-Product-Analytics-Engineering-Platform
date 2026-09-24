import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

class fact_wallet_balance_schema(pa.DataFrameModel):

    wallet_id:Series[int] = pa.Field(ge=1)

    user_id:Series[int] = pa.Field(ge=1)

    current_balance:Series[float] = pa.Field(ge=0, nullable=False)

    last_updated_date:Series[pd.Timestamp] = pa.Field(nullable=False)

    last_updated_date_id:Series[int] = pa.Field(ge=1,nullable=False)

    last_transaction_id:Series[int] = pa.Field(ge=1)

    created_at:Series[pd.Timestamp] = pa.Field(nullable=False)

    updated_at:Series[pd.Timestamp] = pa.Field(nullable=False)


    class Config:
        coerce = True