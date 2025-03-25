# database/events.py

from collections import defaultdict
from .index import with_db_connection


@with_db_connection
def get_club_events(conn, club_id: int):
    """
    Fetches all schedules and their entries (with overrides applied) for a given club_id.
    Returns a list of schedules with their entries as events.
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
    WITH base_entries AS (
        SELECT 
            se.schedule_id,
            se.schedule_entry_id,
            ov.override_id,
            ov.override_date,
            COALESCE(ov.new_team_id, se.team_id) AS team_id,
            COALESCE(ov.new_field_id, se.field_id) AS field_id,
            COALESCE(ov.new_start_time, se.start_time) AS start_time,
            COALESCE(ov.new_end_time, se.end_time) AS end_time,
            se.week_day,
            COALESCE(ov.is_deleted, false) AS is_deleted
        FROM schedule_entries se
        JOIN schedules s ON s.schedule_id = se.schedule_id
        LEFT JOIN active_schedules act ON act.schedule_id = s.schedule_id
        LEFT JOIN schedule_entry_overrides ov 
            ON ov.schedule_entry_id = se.schedule_entry_id
            AND ov.active_schedule_id = act.active_schedule_id
        WHERE s.schedule_id = ANY(%s)
    ),
    one_off_entries AS (
        SELECT 
            act.schedule_id,
            NULL::integer AS schedule_entry_id,
            ov.override_id,
            ov.override_date,
            ov.new_team_id AS team_id,
            ov.new_field_id AS field_id,
            ov.new_start_time AS start_time,
            ov.new_end_time AS end_time,
            NULL::smallint AS week_day,
            ov.is_deleted
        FROM active_schedules act
        JOIN schedule_entry_overrides ov 
            ON ov.active_schedule_id = act.active_schedule_id
        WHERE act.schedule_id = ANY(%s)
          AND ov.schedule_entry_id IS NULL
    )
    SELECT *
    FROM base_entries
    UNION ALL
    SELECT *
    FROM one_off_entries
    ORDER BY schedule_id, week_day, start_time;
    """
    
    cursor.execute(entries_query, (schedule_ids, schedule_ids))
    entries = cursor.fetchall()
    
    entries_by_schedule = defaultdict(list)
    for entry in entries:
        # entry tuple order:
        # 0: schedule_id, 1: schedule_entry_id, 2: override_id,
        # 3: override_date, 4: team_id, 5: field_id,
        # 6: start_time, 7: end_time, 8: week_day, 9: is_deleted
        entries_by_schedule[entry[0]].append({
            'schedule_entry_id': entry[1],
            'override_id': entry[2],
            'override_date': entry[3],
            'team_id': entry[4],
            'field_id': entry[5],
            'start_time': entry[6],
            'end_time': entry[7],
            'week_day': entry[8],
            'is_deleted': entry[9]
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
