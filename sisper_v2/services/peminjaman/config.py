import pymysql

LOAD_TIME = 5

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "kepl_v2_s_peminjaman",
    "cursorclass": pymysql.cursors.DictCursor,
}

REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}
