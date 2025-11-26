import mysql.connector
from mysql.connector import pooling

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "floor_eye",
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="flooreye_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG,
)


def get_connection():
    return connection_pool.get_connection()
