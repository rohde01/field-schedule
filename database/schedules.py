# database/schedules.py

from typing import List, Dict, Optional, Any
from collections import defaultdict
from .index import with_db_connection
from .teams import Team
from .constraints import Constraint, save_constraints
from datetime import datetime, time
from utils import (
    build_time_slots,
    _build_time_slot_mappings,
    parse_time_string,
    minutes_to_time_string,
    time_string_to_time_obj,
)
from database.fields import Field

@with_db_connection
def save_schedule(conn, solver, teams: List[Team], interval_vars: Dict[int, Any],
                 field_name_to_id: Dict[str, int], fields: List[Field],
                 club_id: int = 1, schedule_name: str = "Generated Schedule",
                 constraints_list: Optional[List[Constraint]] = None) -> int:

    """
    Saves the generated schedule and its constraints into the database.
    Returns the schedule_id.
    """
    time_slots, all_days = build_time_slots(fields)
    mappings = _build_time_slot_mappings(time_slots)
    idx_to_time = mappings['idx_to_time']
    time_slots = time_slots
    day_name_to_weekday_index = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

    try:
        cursor = conn.cursor()
        insert_schedule_query = """
        INSERT INTO schedules (club_id, name)
        VALUES (%s, %s)
        RETURNING schedule_id;
        """
        cursor.execute(insert_schedule_query, (club_id, schedule_name))
        schedule_id = cursor.fetchone()[0]

        team_constraints = defaultdict(list)
        if constraints_list:
            for constraint in constraints_list:
                team_constraints[constraint.team_id].append(constraint)

        for team in teams:
            team_id = team.team_id
            if team_id not in interval_vars:
                continue
            for idx_constraint, constraint in enumerate(team_constraints.get(team_id, [])):
                sessions = interval_vars[team_id][idx_constraint]
                parent_schedule_entry_id = None
                for session in sessions:
                    for part_idx, (interval, assigned_combo_var) in enumerate(
                        zip(session['intervals'], session['assigned_combos'])
                    ):
                        start_idx = solver.Value(session['start_vars'][part_idx])
                        end_idx = solver.Value(session['end_vars'][part_idx])
                        assigned_combo_idx = solver.Value(assigned_combo_var)
                        assigned_combo = session['possible_combos'][part_idx][assigned_combo_idx]
                        field_name = assigned_combo[0]
                        field_id = field_name_to_id.get(field_name)
                        
                        # Convert start_idx and end_idx to start_time, end_time, and week_day
                        start_day, start_t = idx_to_time[start_idx]
                        start_time_str = time_slots[start_day][start_t]
                        start_time_minutes = parse_time_string(start_time_str)
                        
                        duration_minutes = (end_idx - start_idx) * 15
                        end_time_minutes = start_time_minutes + duration_minutes
                        end_time_str = minutes_to_time_string(end_time_minutes)
                        
                        start_time_obj = time_string_to_time_obj(start_time_str)
                        end_time_obj = time_string_to_time_obj(end_time_str)
                        
                        week_day = day_name_to_weekday_index[start_day]
                        
                        insert_entry_query = """
                        INSERT INTO schedule_entries (schedule_id, team_id, field_id, start_time, end_time, week_day, parent_schedule_entry_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING schedule_entry_id;
                        """
                        cursor.execute(
                            insert_entry_query,
                            (
                                schedule_id,
                                team_id,
                                field_id,
                                start_time_obj,
                                end_time_obj,
                                week_day,
                                parent_schedule_entry_id
                            )
                        )
                        schedule_entry_id = cursor.fetchone()[0]
                        if parent_schedule_entry_id is None:
                            parent_schedule_entry_id = schedule_entry_id
                            save_constraints(cursor, schedule_entry_id, team_id, constraint)


        conn.commit()
        return schedule_id

    except Exception as e:
        print(f"Error saving schedule: {e}")
        conn.rollback()
        raise e

@with_db_connection
def get_club_schedules(conn, club_id: int):
    """
    Fetches all schedules and their entries for a given club_id.
    Returns a list of schedules with their entries.
    """
    cursor = conn.cursor()
    
    schedules_query = """
    SELECT schedule_id, club_id, name
    FROM schedules
    WHERE club_id = %s;
    """
    cursor.execute(schedules_query, (club_id,))
    schedule_rows = cursor.fetchall()
    
    if not schedule_rows:
        return []
    
    schedule_ids = [row[0] for row in schedule_rows]
    
    entries_query = """
    SELECT schedule_id, schedule_entry_id, team_id, field_id, 
           parent_schedule_entry_id, start_time, 
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
            'parent_schedule_entry_id': entry[4],
            'start_time': entry[5],
            'end_time': entry[6],
            'week_day': entry[7]
        })
    
    return [
        {
            'schedule_id': row[0],
            'club_id': row[1],
            'name': row[2],
            'entries': entries_by_schedule[row[0]]
        }
        for row in schedule_rows
    ]
