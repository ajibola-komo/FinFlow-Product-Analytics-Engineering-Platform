import pandera as pa
import pandas as pd
from pandera.typing import Series


class dim_wallet_schema(pa.DataFrameSchema):

    wallet_id: Series[int] = pa.Field(ge=1)

    user_id: Series[int] = pa.Field(ge=1)

    wallet_currency: Series[str] = pa.Field(checks=pa.Check.isin(['GBP']))

    wallet_created_at: Series[pd.Timestamp] = pa.Field(nullable=False)

    wallet_activated_at: Series[pd.Timestamp] = pa.Field(nullable=True)

    wallet_created_date_id: Series[int] = pa.Field(ge=1)

    wallet_activated_date_id: Series[int] = pa.Field(ge=1)

    created_at: Series[pd.Timestamp]

    last_updated_at: Series[pd.Timestamp]

    class Config:
        coerce=True

