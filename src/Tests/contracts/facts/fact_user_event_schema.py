import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series
import numpy as np

class fact_user_event_schema(pa.DataFrameModel):

    event_id: Series[np.int64] = pa.Field(ge=1)

    user_id:Series[int] = pa.Field(ge=1)

    event_type_id:Series[np.int32] = pa.Field(ge=1,nullable=False)

    wallet_id:Series[int] = pa.Field(ge=1,nullable=True)

    event_time:Series[pd.Timestamp] = pa.Field(nullable=False)

    event_date_id:Series[np.int32] = pa.Field(ge=1,nullable=False)

    device_type:Series[str] = pa.Field(isin=['ios','android'])

    is_money_movement_activity:Series[bool] = pa.Field(nullable=True)

    transaction_type_id:Series[np.int32] = pa.Field(ge=1,nullable=True)

    transaction_id:Series[np.int64] = pa.Field(ge=1,nullable=True)

    investment_id:Series[np.int64] = pa.Field(ge=1,nullable=True)

    class Config:
        coerce:True