from time import sleep
from flask import g
import pymysql
from config import DB_CONFIG


def get_db():
    return pymysql.connect(**DB_CONFIG)


def get_db_conn():
    if 'db' not in g:
        g.db = get_db()
    return g.db


def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()
