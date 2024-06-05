import psycopg2
from psycopg2 import pool
from src.settings import settings


db_pool = None


def init_db_pool():
    global db_pool
    db_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=settings.db_url
    )
    if not db_pool:
        raise Exception("Failed to create connection pool")


def get_db_conn():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def close_db_pool():
    if db_pool:
        db_pool.closeall()
