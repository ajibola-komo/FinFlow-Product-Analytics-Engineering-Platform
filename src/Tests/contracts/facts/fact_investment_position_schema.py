import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

class fact_investment_position_schema(pa.DataFrameModel):

    investment_id:Series[int] = pa.Field(nullable=False, ge=1)

    user_id:Series[int] = pa.Field(nullable=False,ge=1)

    wallet_id:Series[int] = pa.Field(nullable=False,ge=1)

    plan_id:Series[int] = pa.Field(ge=101,le=104,nullable=False)

    amount_invested:Series[float] = pa.Field(nullable=False, ge=1)

    expected_maturity_value:Series[float] = pa.Field(nullable=True,ge=1)

    investment_start_date:Series[pd.Timestamp] = pa.Field(nullable=False)

    investment_start_date_id:Series[int] = pa.Field(ge=1, nullable=False)

    investment_maturity_date: Series[pd.Timestamp] = pa.Field(nullable=True)

    investment_maturity_date_id:Series[int] = pa.Field(ge=1,nullable=True)

    investment_status:Series[str] = pa.Field(isin=['Active','Matured','Redeemed'])

    is_withdrawn_early:Series[bool] = pa.Field(nullable=False)

    penalty_amount:Series[float] = pa.Field(ge=0,nullable=True)

    amount_paid_out:Series[float] = pa.Field(ge=0, nullable=True)

    early_withdrawal_date:Series[pd.Timestamp] = pa.Field(nullable=True)

    early_withdrawal_date_id:Series[int] = pa.Field(ge=1,nullable=True)

    created_at:Series[pd.Timestamp] = pa.Field(nullable=False)

    last_updated_at:Series[pd.Timestamp] = pa.Field(nullable=False)

    class Config:
        coerce = True

