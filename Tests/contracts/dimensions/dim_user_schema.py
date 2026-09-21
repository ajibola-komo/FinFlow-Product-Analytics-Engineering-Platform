import pandera as pa
import pandas as pd
from pandera.typing import Series
from datetime import date


class dim_user_schema(pa.DataFrameSchema):
    user_id: Series[int] = pa.Field(ge=1)

    first_name: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    last_name: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    country: Series[str] = pa.Field(checks=pa.Check.isin(["UK","Ireland"]))

    region: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    city: Series[str] = pa.Field(str_length={"min_value": 2, "max_value": 30})

    email_address: Series[str] = pa.Field(str_length={"min_value": 5, "max_value": 50})

    reported_annual_income: Series[float] = pa.Field(nullable=True, checks=pa.Check.gt(1))

    acquisition_channel: Series[str] = pa.Field(checks=pa.Check.isin(['Organic Search','Paid Social','Referral Program',
                                                                      'Direct Traffic','Paid Search','Partnerships']))
    
    device_type:Series[str] = pa.Field(checks=pa.Check.isin(['ios','android']))

    customer_persona:Series[str] = pa.Field(checks=pa.Check.isin(['Starter Investor', 'Goal-Oriented Saver', 'Wealth Builder', 
                                                                  'Active Investor', 'Capital Preserver']))
    
    kyc_completed:Series[bool] = pa.Field(nullable=False)

    date_of_birth:Series[date] = pa.Field(coerce=True)

    birth_date_id:Series[int] = pa.Field(ge=1)

    signup_date: Series[pd.Timestamp] = pa.Field(coerce=True)

    signup_date_id:Series[int] = pa.Field(ge=1)

    customer_behaviour_segment: Series[str] = pa.Field(checks=pa.Check.isin(['High_Engagement_High_Balance','High_Engagement_Low_Balance', 
                                                                             'Moderate_Engagement_High_Balance','Moderate_Engagement_Low_Balance',
                                                                             'Low_Engagement_High_Balance','Low_Engagement_Low_Balance']))
    
    last_login_at: Series[pd.Timestamp] = pa.Field(coerce=True, nullable=True)

    created_at: Series[pd.Timestamp] = pa.Field(coerce=True)
    
    last_updated_at: Series[pd.Timestamp] = pa.Field(coerce=True)


    class Config:
        coerce = True