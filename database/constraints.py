
from dataclasses import dataclass
from typing import List, Optional, Any
from database.index import with_db_connection

@dataclass
class Constraint:
    team_id: int
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    sessions: int = 0
    length: int = 0
    partial_ses_space_size: Optional[str] = None
    partial_ses_space_cost: Optional[int] = None
    partial_ses_time: Optional[int] = None
    start_time: Optional[str] = None

def get_constraints() -> List[Constraint]:
    """Returns a list of Constraint instances with 'team_id' instead of 'year'."""
    constraints_data = [
        {'team_id': 2, 'required_cost': 250, 'sessions': 3, 'length': 4, 'partial_ses_space_cost': 500, 'partial_ses_time': 2},

        {'team_id': 3, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4, 'partial_ses_space_size': 'half', 'partial_ses_time': 2},
        
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 2},

        {'team_id': 7, 'required_cost': 500, 'sessions': 3, 'length': 4},
        
        {'team_id': 8, 'required_cost': 500, 'sessions': 4, 'length': 4},
        
        {'team_id': 9, 'required_cost': 500, 'sessions': 1, 'length': 5, 'start_time': '16:15'},
    ]
    return [Constraint(**data) for data in constraints_data]

@with_db_connection
def save_constraints(conn, cursor: Any, schedule_entry_id: int, team_id: int, constraint: Constraint) -> None:
    """Saves a constraint to the constraints table."""
    insert_constraint_query = """
    INSERT INTO constraints (
        schedule_entry_id, team_id, required_size, subfield_type, required_cost,
        sessions, length, partial_ses_space_size, partial_ses_space_cost,
        partial_ses_time, start_time
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_constraint_query,
        (schedule_entry_id, team_id, constraint.required_size, constraint.subfield_type,
         constraint.required_cost, constraint.sessions, constraint.length,
         constraint.partial_ses_space_size, constraint.partial_ses_space_cost,
         constraint.partial_ses_time, constraint.start_time)
    )

    