import pandas as pd
import pandera as pa
from pandera.typing import Series
from datetime import date


class dim_date_schema(pa.DataFrameSchema):

    date_id: Series[int] = pa.Field(ge=1)

    full_date: Series[date] = pa.Field(nullable=False)

    year: Series[int] = pa.Field(ge=1)

    quarter: Series[int] = pa.Field(ge=1,le=4)

    month: Series[int] = pa.Field(ge=1,le=12)

    month_name: Series[str] = pa.Field(str_length={"min_value":3, "max_value": 20})

    day: Series[int] = pa.Field(ge=1,le=31)

    week_of_year:Series[int] = pa.Field(ge=1,le=52)

    day_of_week:Series[int] = pa.Field(ge=0,le=6)

    day_name:Series[str] = pd.Field(checks=pa.Check.isin(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']))

    is_weekend:Series[bool] = pd.Field(nullable=False)

    is_month_start: Series[bool] = pd.Field(nullable=False)

    is_month_end: Series[bool] = pd.Field(nullable=False)