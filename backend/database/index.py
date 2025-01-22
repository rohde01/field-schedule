from dotenv import load_dotenv
import os
import psycopg2
from typing import Callable
from functools import wraps

load_dotenv()

connection_string = (
    f"dbname='{os.getenv('DB_NAME')}' user='{os.getenv('DB_USER')}' "
    f"host='{os.getenv('DB_HOST')}' password='{os.getenv('DB_PASSWORD')}'"
)

def with_db_connection(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(connection_string)
            return func(conn, *args, **kwargs)
        finally:
            if conn:
                conn.close()
    return wrapper
