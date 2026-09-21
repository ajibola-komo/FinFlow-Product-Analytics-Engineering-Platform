import pandas as pd
import pandera as pa
from pandera.typing import Series

class fact_user_event_schema(pa.DataFrameSchema):

    event_id: Series[int] = pa.Field(ge=1)

    user_id:Series[int] = pa.Field(ge=1)

    event_type_id:Series[int] = pa.Field(ge=1,nullable=False)

    wallet_id:Series[int] = pa.Field(ge=1)

    event_time:Series[pd.Timestamp] = pa.Field(nullable=False)

    event_date_id:Series[int] = pa.Field(nullable=False, ge=1)

    device_type:Series[str] = pa.Field(checks=pa.Check.isin(['ios','android']))

    is_money_movement_activity:Series[bool] = pa.Field(nullable=False)

    transaction_type_id:Series[int] = pa.Field(ge=1,nullable=True)

    transaction_id:Series[int] = pa.Field(ge=1,nullable=True)

    investment_id:Series[int] = pa.Field(ge=1,nullable=True)