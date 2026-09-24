import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

class fact_transaction_schema(pa.DataFrameModel):

    transaction_id:Series[int] = pa.Field(ge=1)

    wallet_id:Series[int] = pa.Field(ge=1, nullable=False)

    transaction_type_id:Series[int] = pa.Field(ge=1,le=4, nullable=False)

    transaction_amount:Series[float] = pa.Field(ge=1, nullable=False)

    transaction_status:Series[str] = pa.Field(isin=['success','failed','Success','Failed'])

    transaction_timestamp:Series[pd.Timestamp] = pa.Field(nullable=False)

    transaction_date_id:Series[int] = pa.Field(ge=1)

    class Config:
        coerce = True


