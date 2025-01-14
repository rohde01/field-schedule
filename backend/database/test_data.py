
from database.fields import get_fields_by_facility
from dataclasses import dataclass
from typing import List, Optional
from database.index import with_db_connection

@dataclass
class Constraint:
    team_id: int
    sessions: int
    length: int               # in 15-minute blocks
    required_size: str        # '125','250','500','1000'
    start_time: Optional[str] = None  # optional fixed start time



def create_test_data():
    """
    Gets fields from the database and returns a tuple: (list_of_fields, list_of_constraints).
    """
    fields = get_fields_by_facility(4)  # Hardcoded facility_id=4

    constraints = [
        Constraint(team_id=1, sessions=3, length=4, required_size='1000'),# U18-2
        Constraint(team_id=1, sessions=2, length=4, required_size='500'), 

        Constraint(team_id=3, sessions=3, length=4, required_size='500'), # U13

        Constraint(team_id=2, sessions=2, length=4, required_size='1000'), # U10

        Constraint(team_id=4, sessions=3, length=4, required_size='500'), #U12

        Constraint(team_id=7, sessions=4, length=4, required_size='500'), #U16-pige

        Constraint(team_id=5, sessions=2, length=4, required_size='1000'), #U11

        Constraint(team_id=6, sessions=4, length=4, required_size='500'), #U18

        
        Constraint(team_id=100, sessions=3, length=4, required_size='500'),# U18-2
        Constraint(team_id=100, sessions=2, length=4, required_size='250'), 

        Constraint(team_id=900, sessions=3, length=4, required_size='250'), # U13

        Constraint(team_id=200, sessions=2, length=4, required_size='500'), # U10

        Constraint(team_id=400, sessions=3, length=4, required_size='250'), #U12

        Constraint(team_id=700, sessions=4, length=4, required_size='250'), #U16-pige

        Constraint(team_id=500, sessions=2, length=4, required_size='500'), #U11

        Constraint(team_id=600, sessions=4, length=4, required_size='250'), #U18


        Constraint(team_id=50, sessions=3, length=4, required_size='1000'),# U18-2
        Constraint(team_id=50, sessions=2, length=4, required_size='500'), 

        Constraint(team_id=35, sessions=3, length=4, required_size='500'), # U13

        Constraint(team_id=78, sessions=2, length=4, required_size='1000'), # U10

        Constraint(team_id=89, sessions=3, length=4, required_size='500'), #U12

        Constraint(team_id=98, sessions=4, length=4, required_size='500'), #U16-pige

        Constraint(team_id=32, sessions=2, length=4, required_size='1000'), #U11

        Constraint(team_id=53, sessions=4, length=4, required_size='500'), #U18
    ]

    return fields, constraints


@with_db_connection
def save_schedule(conn, solution: List[dict], club_id: int, facility_id: int, name: str) -> int:
    """
    Save the generated schedule to the database.
    
    Args:
        conn: Database connection from decorator
        solution: List of scheduled sessions
        club_id: ID of the club the schedule belongs to
        facility_id: ID of the facility
        name: Name of the schedule
        
    Returns:
        schedule_id: ID of the created schedule
    """
    # Insert into schedules table
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO schedules (club_id, name, facility_id)
            VALUES (%s, %s, %s)
            RETURNING schedule_id
            """,
            (club_id, name, facility_id)
        )
        schedule_id = cur.fetchone()[0]
        
        # Insert all entries
        for entry in solution:
            # Convert day of week from string to integer (0 = Monday, 6 = Sunday)
            day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
            week_day = day_mapping[entry['day_of_week']]
            
            cur.execute(
                """
                INSERT INTO schedule_entries 
                (schedule_id, team_id, field_id, start_time, end_time, week_day)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    schedule_id,
                    entry['team_id'],
                    entry['field_id'],
                    entry['start_time'],
                    entry['end_time'],
                    week_day
                )
            )
        
        conn.commit()
        return schedule_id
