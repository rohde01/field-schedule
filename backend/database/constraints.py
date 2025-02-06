from typing import List, Any
from database.index import with_db_connection
from models.schedule import Constraint

@with_db_connection
def get_constraints(conn, club_id: int) -> List[Constraint]:
    """Returns a list of Constraint instances for a specific club from the database."""
    cursor = conn.cursor()
    select_query = """
    SELECT constraint_id, schedule_entry_id, team_id, club_id, 
           required_cost, sessions, length, partial_field, partial_cost,
           partial_time, start_time, day_of_week
    FROM constraints
    WHERE club_id = %s
    """
    cursor.execute(select_query, (club_id,))
    rows = cursor.fetchall()
    
    constraints = []
    for row in rows:
        constraint_data = {
            'constraint_id': row[0],
            'schedule_entry_id': row[1],
            'team_id': row[2],
            'club_id': row[3],
            'required_cost': row[4],
            'sessions': row[5],
            'length': row[6],
            'partial_field': row[7],
            'partial_cost': row[8],
            'partial_time': row[9],
            'start_time': row[10],
            'day_of_week': row[11]
        }
        constraints.append(Constraint(**constraint_data))
    cursor.close()
    return constraints

def save_constraints(cursor: Any, schedule_entry_id: int, team_id: int, constraint: Constraint, club_id: int) -> None:
    """Saves a constraint to the constraints table."""
    insert_constraint_query = """
    INSERT INTO constraints (
        schedule_entry_id, team_id, club_id, sessions, length,
        required_cost, required_field, partial_field, partial_cost,
        partial_time, start_time, day_of_week
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_constraint_query,
        (
            schedule_entry_id, 
            team_id, 
            club_id,
            constraint.sessions,
            constraint.length,
            constraint.required_cost,
            constraint.required_field,
            constraint.partial_field,
            constraint.partial_cost,
            constraint.partial_time,
            constraint.start_time,
            constraint.day_of_week
        )
    )
