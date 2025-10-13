# Project modules
from decouple import config

# -----------------------------------
# Env id
# -----------------------------------
ENV_POSSIBLE_OPTIONS = (
    'local',
    'prod',
)
ENV_ID = config("EATLY_ENV_ID", cast=str)
SECRET_KEY = 'django-insecure-7=w9-!6%euxf#t6xb4lv_ln7ag$6vdb2i+k)0hhp5&)k4w+dgo'