from psycopg2.extras import RealDictCursor
from .index import with_db_connection

@with_db_connection
def create_club(conn, club_data: dict):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO clubs (name)
            VALUES (%(name)s)
            RETURNING club_id, name
        """, club_data)
        conn.commit()
        return cur.fetchone()

@with_db_connection
def add_user_to_club(conn, user_id: int, club_id: int, is_primary: bool = False):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO user_club (user_id, club_id, is_primary)
            VALUES (%s, %s, %s)
            RETURNING user_id, club_id, is_primary, added_at
        """, (user_id, club_id, is_primary))
        conn.commit()
        return cur.fetchone()

@with_db_connection
def get_club(conn, club_id: int):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM clubs WHERE club_id = %s", (club_id,))
        return cur.fetchone()
