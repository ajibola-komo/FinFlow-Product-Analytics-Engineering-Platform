import pandas as pd
import pandera as pa
from pandera.typing import Series

class fact_investment_position_schema(pa.DataFrameSchema):

    investment_id:Series[int] = pa.Field(nullable=False, ge=1)

    user_id:Series[int] = pa.Field(nullable=False,ge=1)

    wallet_id:Series[int] = pa.Field(nullable=False,ge=1)

    plan_id:Series[int] = pa.Field(nullable=False,ge=101,le=104)

    amount_invested:Series[float] = pa.Field(nullable=False, ge=1)

    expected_maturity_value:Series[float] = pa.Field(nullable=True,ge=1)

    investment_start_date:Series[pd.Timestamp] = pa.Field(nullable=False)

    investment_start_date_id:Series[int] = pa.Field(ge=1)

    investment_maturity_date: Series[pd.Timestamp] = pa.Field(nullable=True)

    investment_maturity_date_id:Series[int] = pa.Field(ge=1)

    investment_status:Series[str] = pa.Field(checks=pa.Check.isin(['active','matured','redeemed']))

    is_withdrawn_early:Series[bool] = pa.Field(nullable=False)

    penalty_amount:Series[float] = pa.Field(ge=0,nullable=True)

    amount_paid_out:Series[float] = pa.Field(ge=0, nullable=True)

    early_withdrawal_date:Series[pd.Timestamp] = pa.Field(nullable=True)

    early_withdrawal_date_id:Series[int] = pa.Field(ge=1)

    created_at:Series[pd.Timestamp] = pa.Field(nullable=False)

    last_updated_at:Series[pd.Timestamp] = pa.Field(nullable=False)

