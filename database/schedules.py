# database/schedules.py

from typing import List, Dict, Optional, Any
from collections import defaultdict
from .index import with_db_connection
from .teams import Team
from .constraints import Constraint, save_constraints

@with_db_connection
def save_schedule(conn, solver, teams: List[Team], interval_vars: Dict[int, Any],
                 field_name_to_id: Dict[str, int], club_id: int = 1,
                 schedule_name: str = "Generated Schedule",
                 constraints_list: Optional[List[Constraint]] = None) -> int:
    """
    Saves the generated schedule and its constraints into the database.
    Returns the schedule_id.
    """
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

                        insert_entry_query = """
                        INSERT INTO schedule_entries (schedule_id, team_id, field_id, session_start, session_end, parent_schedule_entry_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING schedule_entry_id;
                        """
                        cursor.execute(
                            insert_entry_query,
                            (
                                schedule_id,
                                team_id,
                                field_id,
                                start_idx,
                                end_idx,
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
def get_schedule_entries(conn, schedule_id: int) -> List[tuple]:
    cursor = conn.cursor()
    query = """
    SELECT se.team_id, se.field_id, se.session_start, se.session_end, 
           se.parent_schedule_entry_id
    FROM schedule_entries se
    WHERE se.schedule_id = %s
    """
    cursor.execute(query, (schedule_id,))
    return cursor.fetchall()