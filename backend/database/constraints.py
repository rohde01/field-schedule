from dataclasses import dataclass
from typing import List, Optional, Any, Literal
from database.index import with_db_connection


@dataclass
class Constraint:
    team_id: int
    sessions: int
    length: int
    day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]]
    club_id: Optional[int] = None
    constraint_id: Optional[int] = None
    schedule_entry_id: Optional[int] = None
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    start_time: Optional[str] = None
    partial_field: Optional[str] = None
    partial_cost: Optional[int] = None
    partial_time: Optional[int] = None

    def __init__(self, team_id: int, sessions: int, length: int, day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None, **kwargs):
        self.team_id = team_id
        self.sessions = sessions
        self.length = length
        self.day_of_week = day_of_week
        for key, value in kwargs.items():
            setattr(self, key, value)

@with_db_connection
def get_constraints(conn, club_id: int) -> List[Constraint]:
    """Returns a list of Constraint instances for a specific club from the database."""
    cursor = conn.cursor()
    select_query = """
    SELECT constraint_id, schedule_entry_id, team_id, club_id, required_size, subfield_type, 
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
            'required_size': row[4],
            'subfield_type': row[5],
            'required_cost': row[6],
            'sessions': row[7],
            'length': row[8],
            'partial_field': row[9],
            'partial_cost': row[10],
            'partial_time': row[11],
            'start_time': row[12],
            'day_of_week': row[13]
        }
        constraints.append(Constraint(**constraint_data))
    cursor.close()
    return constraints

def save_constraints(cursor: Any, schedule_entry_id: int, team_id: int, constraint: Constraint, club_id: int) -> None:
    """Saves a constraint to the constraints table."""
    insert_constraint_query = """
    INSERT INTO constraints (
        schedule_entry_id, team_id, club_id, required_size, subfield_type, required_cost,
        sessions, length, partial_field, partial_cost,
        partial_time, start_time, day_of_week
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_constraint_query,
        (schedule_entry_id, team_id, constraint.club_id, constraint.required_size, constraint.subfield_type,
         constraint.required_cost, constraint.sessions, constraint.length,
         constraint.partial_field, constraint.partial_cost,
         constraint.partial_time, constraint.start_time, constraint.day_of_week)
    )
