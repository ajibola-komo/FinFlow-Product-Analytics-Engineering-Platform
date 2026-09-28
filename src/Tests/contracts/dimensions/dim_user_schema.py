from duckdb import df
import pandera.pandas as pa
import pandas as pd
from pandera.typing import Series
from datetime import date
from src.config.constants import CURRENT_DATE, CURRENT_YEAR


class dim_user_schema(pa.DataFrameModel):
    user_id: Series[int] = pa.Field(ge=1)

    first_name: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    last_name: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    country: Series[str] = pa.Field(isin=["UK","Ireland"])

    region: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    city: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    email_address: Series[str] = pa.Field(str_length={"min_value": 5, "max_value": 50},unique=True, nullable=False,regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    reported_annual_income: Series[float] = pa.Field(nullable=True, gt=0)

    acquisition_channel: Series[str] = pa.Field(isin=['Organic Search','Paid Social','Referral Program',
                                                                      'Direct Traffic','Paid Search','Partnerships'])
    
    device_type:Series[str] = pa.Field(isin=['ios','android'])

    customer_persona:Series[str] = pa.Field(isin=['Starter Investor', 'Goal-Oriented Saver', 'Wealth Builder', 
                                                                  'Active Investor', 'Capital Preserver'])
    
    kyc_completed:Series[bool] = pa.Field(nullable=False)

    date_of_birth:Series[date] = pa.Field(coerce=True)

    birth_date_id:Series[int] = pa.Field(ge=1)

    signup_date: Series[pd.Timestamp] = pa.Field(coerce=True)

    signup_date_id:Series[int] = pa.Field(ge=1)

    customer_behaviour_segment: Series[str] = pa.Field(isin=['High_Engagement_High_Balance','High_Engagement_Low_Balance', 
                                                                             'Moderate_Engagement_High_Balance','Moderate_Engagement_Low_Balance',
                                                                             'Low_Engagement_High_Balance','Low_Engagement_Low_Balance'])
    
    last_login_at: Series[pd.Timestamp] = pa.Field(coerce=True, nullable=True)

    created_at: Series[pd.Timestamp] = pa.Field(coerce=True)
    
    last_updated_at: Series[pd.Timestamp] = pa.Field(coerce=True)

    @pa.dataframe_check
    def min_age_compliance(cls, df:pd.DataFrame) -> pd.Series:

        dob = pd.to_datetime(df['date_of_birth'])
        
        age = (
        CURRENT_DATE.year - dob.dt.year - (
            (dob.dt.month > CURRENT_DATE.month)
            |
            (
                (dob.dt.month == CURRENT_DATE.month)
                & (dob.dt.day > CURRENT_DATE.day)
            )
        )
    )
        
        return age >= 18

    @pa.dataframe_check
    def min_age_at_signup(cls, df: pd.DataFrame) -> pd.Series:

        dob = pd.to_datetime(df["date_of_birth"])
        signup_date = pd.to_datetime(df["signup_date"])

        age_at_signup = (
        signup_date.dt.year
        - dob.dt.year
        - (
            (signup_date.dt.month < dob.dt.month)
            |
            (
                (signup_date.dt.month == dob.dt.month)
                & (signup_date.dt.day < dob.dt.day)
            )
        )
    )

        return age_at_signup >= 18

    @pa.dataframe_check
    def date_id_format_matches_date(cls, df:pd.DataFrame) -> pd.Series[bool]:

        dob = df['date_of_birth']
        birth_date_id = df['birth_date_id']

        signup_date = df['signup_date']
        signup_date_id = df['signup_date_id']

        return (birth_date_id == dob.dt.strftime("%Y%m%d").astype(int)) & (signup_date_id == signup_date.dt.strftime("%Y%m%d").astype(int))



    class Config:
        coerce = True