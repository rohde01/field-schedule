from dataclasses import dataclass
from typing import List, Optional, Any
from database.index import with_db_connection

@dataclass
class Constraint:
    team_id: int
    club_id: int
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    sessions: int = 0
    length: int = 0
    partial_ses_space_size: Optional[str] = None
    partial_ses_space_cost: Optional[int] = None
    partial_ses_time: Optional[int] = None
    start_time: Optional[str] = None

@with_db_connection
def get_constraints(conn, club_id: int) -> List[Constraint]:
    """Returns a list of Constraint instances for a specific club from the database."""
    cursor = conn.cursor()
    select_query = """
    SELECT team_id, club_id, required_size, subfield_type, required_cost,
           sessions, length, partial_ses_space_size, partial_ses_space_cost,
           partial_ses_time, start_time
    FROM constraints
    WHERE club_id = %s
    """
    cursor.execute(select_query, (club_id,))
    rows = cursor.fetchall()
    
    constraints = []
    for row in rows:
        constraint_data = {
            'team_id': row[0],
            'club_id': row[1],
            'required_size': row[2],
            'subfield_type': row[3],
            'required_cost': row[4],
            'sessions': row[5],
            'length': row[6],
            'partial_ses_space_size': row[7],
            'partial_ses_space_cost': row[8],
            'partial_ses_time': row[9],
            'start_time': row[10]
        }
        constraints.append(Constraint(**constraint_data))
    cursor.close()
    return constraints

@with_db_connection
def save_constraints(conn, cursor: Any, schedule_entry_id: int, team_id: int, constraint: Constraint) -> None:
    """Saves a constraint to the constraints table."""
    insert_constraint_query = """
    INSERT INTO constraints (
        schedule_entry_id, team_id, club_id, required_size, subfield_type, required_cost,
        sessions, length, partial_ses_space_size, partial_ses_space_cost,
        partial_ses_time, start_time
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_constraint_query,
        (schedule_entry_id, team_id, constraint.club_id, constraint.required_size, constraint.subfield_type,
         constraint.required_cost, constraint.sessions, constraint.length,
         constraint.partial_ses_space_size, constraint.partial_ses_space_cost,
         constraint.partial_ses_time, constraint.start_time)
    )

