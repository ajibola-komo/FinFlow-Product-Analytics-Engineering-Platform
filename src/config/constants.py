from datetime import date, datetime, time, timedelta, timezone

TIMEZONE = "UTC"

TODAY = date.today()

# Signup range
DEFAULT_SIGNUP_START_DATE = date(2016, 1, 1)
DEFAULT_SIGNUP_END_DATE = TODAY - timedelta(days=1)

DEFAULT_SIGNUP_START_TIMESTAMP = datetime.combine(DEFAULT_SIGNUP_START_DATE, time.min, tzinfo=timezone.utc)
DEFAULT_SIGNUP_END_TIMESTAMP = datetime.combine(DEFAULT_SIGNUP_END_DATE, time.max, tzinfo=timezone.utc)

# Transaction range
CURRENT_YEAR = TODAY.year
CURRENT_MONTH = TODAY.month

DEFAULT_TRANSACTION_START_DATE = date(CURRENT_YEAR - 3, 1, 1)
DEFAULT_TRANSACTION_END_DATE = TODAY - timedelta(days=1)

DEFAULT_TRANSACTION_START_TIMESTAMP = datetime.combine(DEFAULT_TRANSACTION_START_DATE, time.min, tzinfo=timezone.utc)
DEFAULT_TRANSACTION_END_TIMESTAMP = datetime.combine(DEFAULT_TRANSACTION_END_DATE, time.max, tzinfo=timezone.utc)


#dim_user constants
EMAIL_DOMAIN = ["@example.com","abc.com","xyz.com","test.com","demo.com"]
GENDER = ["Male", "Female", "Other"]
GENDER_WEIGHTS = [0.48, 0.48, 0.04]  # Assuming a distribution of 48%

LOCATION_MAP = {
    "UK": {
        "regions": {"Greater London":{
            "region_weight": 0.3,  # Assuming 30% of UK users are from Greater London
            "cities": ["London"],
            "weights": [1.0]  # Assuming all users in Greater London are from London
        }, 
        "Wales": {
            "region_weight": 0.15,
            "cities": ["Cardiff", "Swansea", "Newport"],
            "weights": [0.5, 0.3, 0.2]
        },
        "Scotland": {
            "region_weight": 0.15,
            "cities": ["Edinburgh", "Glasgow", "Aberdeen"],
            "weights": [0.4, 0.4, 0.2]
        },
        "North West": {
            "region_weight": 0.1,
            "cities": ["Manchester", "Liverpool", "Chester"],
            "weights": [0.5, 0.3, 0.2]
        },
        "South East": {
            "region_weight": 0.1,
            "cities": ["Brighton", "Reading", "Southampton"],
            "weights": [0.4, 0.35, 0.25]
        },
        "Midlands": {
            "region_weight": 0.2,
            "cities": ["Birmingham", "Coventry", "Leicester", "Nottingham"],
            "weights": [0.45, 0.2, 0.2, 0.15]
        }
    }},
    "Ireland": {
        "regions": {"Dublin Region":{
            "region_weight": 0.4,  # Assuming 40% of Ireland users are from Dublin Region   
            "cities": ["Dublin"],
            "weights": [1.0]  # Assuming all users in Dublin Region are from Dublin
        }, "Rest of Ireland": {
            "region_weight": 0.6,
            "cities": ["Cork", "Galway", "Limerick", "Waterford"],
            "weights": [0.4, 0.25, 0.2, 0.15]
        }}
    }
}

COUNTRIES_LIST = ["UK", "Ireland"]
COUNTRIES_WEIGHTS = [0.8, 0.2]  # Assuming 80% of users are from the UK and 20% from Ireland
AGE_BUCKETS = ["18-24", "25-34", "35-44", "45-54", "55-65"]
AGE_WEIGHTS = [0.20, 0.35, 0.25, 0.15, 0.05]
CUSTOMER_PERSONA_MAP = {
    'Starter Investor':{
        'age_range':[18,31],
        'income_range':[18000,50000]
    },
    'Goal-Oriented Saver':{
        'age_range':[25,56],
        'income_range':[25000,90000]
    },
    'Wealth Builder':{
        'age_range':[25,61],
        'income_range':[40000,150000]
    },
    'Active Investor':{
        'age_range':[25,66],
        'income_range':[60000,120000]
    },
    'Capital Preserver':{
        'age_range':[45,66],
        'income_range':[50000,85000]
    }
}
CUSTOMER_PERSONAS = list(CUSTOMER_PERSONA_MAP.keys()) 
CUSTOMER_PERSONA_WEIGHTS = [0.25,0.3,0.25,0.1,0.1]

ACQUISITION_CHANNELS = ['Organic Search','Paid Social','Referral Program','Direct Traffic','Paid Search','Partnerships']
CHANNEL_WEIGHTS = [0.25,0.2,0.2,0.15,0.1,0.1]

#events simulation
POST_SIGN_UP_IMMEDIATE_LOGINS = 0.45
POST_SIGN_UP_SAME_DAY_LOGINS = 0.25
POST_SIGN_UP_DELAYED_LOGINS = 0.3

IMMEDIATE_LOGINS_TIME_FRAME = [60,300] #seconds
SAME_DAY_LOGINS_TIME_FRAME = [18000,86400] #seconds
DELAYED_LOGINS_TIME_FRAME = [86400,604800] #seconds
UNACTIVATED_USERS_TIME_FRAME = [600,1209600] #seconds
WALLET_ACTIVATION_SUBSET = 0.6
IMMEDIATE_ACTIVATION_SUBSET = 0.2

IMMEDIATE_WALLET_ACTIVATION_TIME_FRAME = [600,3600] #seconds - between 10 minutes and 1 hour
DELAYED_WALLET_ACTIVATION_LOGIN_TIME_FRAME = [3600,10080] #seconds - between 1 hour and 7 days
DELAYED_WALLET_ACTIVATION_TIME_FRAME = [600,3600] #seconds - between 10 minutes and 1 hour



