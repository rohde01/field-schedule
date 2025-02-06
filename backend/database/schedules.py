# database/schedules.py

from typing import List, Optional
from collections import defaultdict
from .index import with_db_connection
from database.constraints import save_constraints


@with_db_connection
def save_schedule(conn, solution: List[dict], club_id: int, facility_id: int, name: str, constraints_list=None) -> int:
    """
    Save the generated schedule and its constraints to the database.
    
    Args:
        conn: Database connection from decorator
        solution: List of scheduled sessions
        club_id: ID of the club the schedule belongs to
        facility_id: ID of the facility
        name: Name of the schedule
        constraints_list: Optional list of constraints to save
        
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
        
        entries_by_team = defaultdict(list)
        for entry in solution:
            entries_by_team[entry['team_id']].append(entry)

        parent_entries = {}
        team_first_entries = {}
        
        # Insert all entries
        for entry in solution:
            day_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
            week_day = day_mapping[entry['day_of_week']]
            
            parent_id = None
            entry_key = (entry['team_id'], entry['start_time'], entry['day_of_week'])
            if entry_key in parent_entries:
                parent_id = parent_entries[entry_key]
            
            cur.execute(
                """
                INSERT INTO schedule_entries 
                (schedule_id, team_id, field_id, start_time, end_time, week_day)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING schedule_entry_id
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
            entry_id = cur.fetchone()[0]
            
            if entry_key not in parent_entries:
                parent_entries[entry_key] = entry_id
                
            if entry['team_id'] not in team_first_entries:
                team_first_entries[entry['team_id']] = entry_id

        if constraints_list:
            for constraint in constraints_list:
                if constraint.team_id in team_first_entries:
                    save_constraints(cur, team_first_entries[constraint.team_id], 
                                  constraint.team_id, constraint, club_id)
        
        conn.commit()
        return schedule_id

@with_db_connection
def get_club_schedules(conn, club_id: int):
    """
    Fetches all schedules and their entries for a given club_id.
    Returns a list of schedules with their entries.
    """
    cursor = conn.cursor()
    
    schedules_query = """
    SELECT schedule_id, club_id, name, facility_id
    FROM schedules
    WHERE club_id = %s;
    """
    cursor.execute(schedules_query, (club_id,))
    schedule_rows = cursor.fetchall()
    
    if not schedule_rows:
        return []
    
    schedule_ids = [row[0] for row in schedule_rows]
    
    entries_query = """
    SELECT schedule_id, schedule_entry_id, team_id, field_id, start_time, 
           end_time, week_day
    FROM schedule_entries
    WHERE schedule_id = ANY(%s)
    ORDER BY schedule_id, week_day, start_time;
    """
    cursor.execute(entries_query, (schedule_ids,))
    entries = cursor.fetchall()
    
    entries_by_schedule = defaultdict(list)
    for entry in entries:
        entries_by_schedule[entry[0]].append({
            'schedule_entry_id': entry[1],
            'team_id': entry[2],
            'field_id': entry[3],
            'start_time': entry[4],
            'end_time': entry[5],
            'week_day': entry[6]
        })
    
    return [
        {
            'schedule_id': row[0],
            'club_id': row[1],
            'name': row[2],
            'facility_id': row[3],
            'entries': entries_by_schedule[row[0]]
        }
        for row in schedule_rows
    ]

@with_db_connection
def delete_schedule(conn, schedule_id: int):
    """
    Deletes a schedule from the schedules table. Entries and constraints are automatically deleted on cascade.
    """
    cursor = conn.cursor()
    
    delete_query = """
    DELETE FROM schedules
    WHERE schedule_id = %s
    RETURNING schedule_id;
    """
    cursor.execute(delete_query, (schedule_id,))
    success = cursor.fetchone() is not None
    conn.commit()
    return success

@with_db_connection
def get_schedule_club_id(conn, schedule_id: int) -> Optional[int]:
    """Gets the club_id for a given schedule_id"""
    cursor = conn.cursor()
    query = "SELECT club_id FROM schedules WHERE schedule_id = %s"
    cursor.execute(query, (schedule_id,))
    result = cursor.fetchone()
    return result[0] if result else None
