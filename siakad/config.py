import pymysql

LOAD_TIME = 0

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "kepl_siakad",
    "cursorclass": pymysql.cursors.DictCursor
}
