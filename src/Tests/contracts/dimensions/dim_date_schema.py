import pandera.pandas as pa
from pandera.typing import Series
from datetime import date
import pandas as pd


class dim_date_schema(pa.DataFrameModel):

    date_id: Series[int] = pa.Field(ge=1,nullable=False)

    full_date: Series[date] = pa.Field(nullable=False)

    year: Series[int] = pa.Field(ge=1,nullable=False)

    quarter: Series[int] = pa.Field(ge=1,le=4,nullable=False)

    month: Series[int] = pa.Field(ge=1,le=12,nullable=False)

    month_name: Series[str] = pa.Field(str_length={"min_value":3, "max_value": 20},nullable=False)

    day: Series[int] = pa.Field(ge=1,le=31,nullable=False)

    week_of_year:Series[int] = pa.Field(ge=1,le=53,nullable=False)

    day_of_week:Series[int] = pa.Field(ge=0,le=6,nullable=False)

    day_name:Series[str] = pa.Field(isin=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],nullable=False)

    is_weekend:Series[bool] = pa.Field(nullable=False)

    is_month_start: Series[bool] = pa.Field(nullable=False)

    is_month_end: Series[bool] = pa.Field(nullable=False)

    @pa.dataframe_check
    def date_id_matches_full_date(cls, df:pd.DataFrame):

        d_id = df['date_id']
        f_date = df['full_date']

        return d_id == f_date.df.strftime("%Y%m%d").astype(int)


    class Config:
        coerce=True