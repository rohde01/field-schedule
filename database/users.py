from psycopg2.extras import RealDictCursor
from .index import with_db_connection
from datetime import datetime
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@with_db_connection
def create_user(conn, user_data: dict):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        user_data['password_hash'] = hash_password(user_data['password'])
        del user_data['password']
        
        columns = ', '.join(user_data.keys())
        values = ', '.join([f'%({k})s' for k in user_data.keys()])
        
        query = f"""
            INSERT INTO users ({columns})
            VALUES ({values})
            RETURNING user_id, username, email, first_name, last_name, role, created_at
        """
        cur.execute(query, user_data)
        conn.commit()
        return cur.fetchone()

@with_db_connection
def get_user(conn, user_id: int):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT user_id, username, email, first_name, last_name, role, created_at, is_active
            FROM users WHERE user_id = %s
        """, (user_id,))
        return cur.fetchone()

@with_db_connection
def update_user(conn, user_id: int, user_data: dict):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if 'password' in user_data:
            user_data['password_hash'] = hash_password(user_data['password'])
            del user_data['password']
        
        user_data['updated_at'] = datetime.now()
        set_values = ', '.join([f"{k} = %({k})s" for k in user_data.keys()])
        
        query = f"""
            UPDATE users SET {set_values}
            WHERE user_id = %(user_id)s
            RETURNING user_id, username, email, first_name, last_name, role
        """
        cur.execute(query, {**user_data, 'user_id': user_id})
        conn.commit()
        return cur.fetchone()
