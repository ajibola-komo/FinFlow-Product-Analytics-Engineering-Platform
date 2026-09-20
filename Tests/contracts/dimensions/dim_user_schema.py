import pandera as pa
import pandas as pd
from pandera.typing import Series


class dim_user_schema(pa.SchemaModel):
    user_id: Series[int] = pa.Field(ge=1)
    username: Series[str] = pa.Field(str_length={"min_value": 3, "max_value": 50})
    email: Series[str] = pa.Field(str_length={"min_value": 5, "max_value": 100})
    created_at: Series[pd.Timestamp] = pa.Field(coerce=True)
    is_active: Series[bool] = pa.Field()

    class Config:
        coerce = True