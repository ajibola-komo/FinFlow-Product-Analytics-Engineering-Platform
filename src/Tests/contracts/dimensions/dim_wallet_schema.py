import pandera.pandas as pa
import pandas as pd
from pandera.typing import Series


class dim_wallet_schema(pa.DataFrameModel):

    wallet_id: Series[int] = pa.Field(ge=1)

    user_id: Series[int] = pa.Field(ge=1)

    wallet_currency: Series[str] = pa.Field(isin=['GBP'])

    wallet_created_at: Series[pd.Timestamp] = pa.Field(nullable=False)

    wallet_activated_at: Series[pd.Timestamp] = pa.Field(nullable=True)

    wallet_created_date_id: Series[int] = pa.Field(ge=1)

    wallet_activated_date_id: Series[int] = pa.Field(ge=1,nullable=True)

    created_at: Series[pd.Timestamp] = pa.Field(nullable=False)

    last_updated_at: Series[pd.Timestamp] = pa.Field(nullable=False)

    class Config:
        coerce=True

