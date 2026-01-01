from time import sleep

import pymysql
from config import DB_CONFIG, SIMULATED_LOAD_TIME

def get_db():
    sleep(SIMULATED_LOAD_TIME)
    return pymysql.connect(**DB_CONFIG)
