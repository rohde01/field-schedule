from psycopg2.extras import RealDictCursor
from .index import with_db_connection
from datetime import datetime
import bcrypt
import logging

logger = logging.getLogger(__name__)

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

@with_db_connection
def authenticate_user(conn, username: str, password: str):
    """Authenticate user by username and password."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        return None

@with_db_connection
def get_user_by_username(conn, username: str):
    """Retrieve user information by username."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT user_id, username, email, first_name, last_name, role, created_at, is_active
            FROM users WHERE username = %s
        """, (username,))
        return cur.fetchone()

@with_db_connection
def check_existing_credentials(conn, username: str, email: str):
    """Check if username or email already exists."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT username, email FROM users 
            WHERE username = %s OR email = %s
        """, (username, email))
        return cur.fetchone()

@with_db_connection
def get_user_primary_club(conn, user_id: int):
    """Get user's primary club ID."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT club_id FROM user_club 
            WHERE user_id = %s AND is_primary = true
        """, (user_id,))
        result = cur.fetchone()
        return result['club_id'] if result else None
    
@with_db_connection
def user_belongs_to_club(conn, user_id: int, club_id: int) -> bool:
    """
    Check if a given user is associated with a specified club.
    """
    logger.info(f"Checking if user_id={user_id} belongs to club_id={club_id}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1 
            FROM user_club 
            WHERE user_id = %s AND club_id = %s
        """, (user_id, club_id))
        result = cur.fetchone() is not None
        logger.info(f"User {user_id} {'belongs' if result else 'does not belong'} to club {club_id}")
        return result
