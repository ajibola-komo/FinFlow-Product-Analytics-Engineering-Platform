import pandas as pd
import pandera as pa
from pandera.typing import Series

class fact_transaction_schema(pa.DataFrameSchema):

    transaction_id:Series[int] = pa.Field(ge=1)

    wallet_id:Series[int] = pa.Field(ge=1, nullable=False)

    transaction_types_id:Series[int] = pa.Field(ge=1,le=4, nullable=False)

    transaction_amount:Series[float] = pa.Field(ge=1, nullable=False)

    transaction_status:Series[str] = pa.Field(checks=pa.Check.isin(['success','failed']))

    transaction_timestamp:Series[pd.Timestamp] = pa.Field(nullable=False)

    transaction_date_id:Series[int] = pa.Field(ge=1)

    class Config:
        coerce = True


