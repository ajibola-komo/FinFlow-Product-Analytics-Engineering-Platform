from datetime import timedelta, datetime, date, time

# Timezone
TIMEZONE = "UTC"
# Default Time Range for Data Processing
DEFAULT_START_DATE = date(2023, 1, 1)
DEFAULT_END_DATE = date.today(TIMEZONE)
# Time Range for Data Processing
DEFAULT_START_TIMESTAMP = datetime.combine(DEFAULT_START_DATE, time.min)
DEFAULT_END_TIMESTAMP = datetime.combine(DEFAULT_END_DATE, time.max)
