# database/events.py

from collections import defaultdict
from typing import Optional, Any, Dict
from datetime import date, time
from .index import with_db_connection

@with_db_connection
def get_club_events(conn, club_id: int):
    """
    Fetches all schedules and their entries (with overrides applied) for a given club_id.
    Returns a list of schedules with their entries as events.
    Each event is a dict matching the Event model:
      - schedule_entry_id, override_id, override_date, team_id, field_id,
        start_time, end_time, week_day, is_deleted.
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
            NULL::integer as override_id,
            NULL::date as override_date,
            se.team_id,
            se.field_id,
            se.start_time::text,
            se.end_time::text,
            se.week_day,
            false as is_deleted
        FROM schedule_entries se
        WHERE se.schedule_id = ANY(%s)
    ),
    overridden_entries AS (
        SELECT 
            s.schedule_id,
            se.schedule_entry_id,
            ov.override_id,
            ov.override_date,
            COALESCE(ov.new_team_id, se.team_id) AS team_id,
            COALESCE(ov.new_field_id, se.field_id) AS field_id,
            COALESCE(ov.new_start_time::text, se.start_time::text) AS start_time,
            COALESCE(ov.new_end_time::text, se.end_time::text) AS end_time,
            se.week_day,
            ov.is_deleted
        FROM schedule_entries se
        JOIN schedules s ON s.schedule_id = se.schedule_id
        JOIN active_schedules act ON act.schedule_id = s.schedule_id
        JOIN schedule_entry_overrides ov 
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
            ov.new_start_time::text AS start_time,
            ov.new_end_time::text AS end_time,
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
    FROM overridden_entries
    UNION ALL
    SELECT *
    FROM one_off_entries
    ORDER BY schedule_id, week_day, start_time;
    """
    
    cursor.execute(entries_query, (schedule_ids, schedule_ids, schedule_ids))
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
            'override_date': entry[3].isoformat() if entry[3] else None,
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


@with_db_connection
def create_event_override(
    conn,
    active_schedule_id: int,
    override_date: date,
    new_start_time: time,
    new_end_time: time,
    new_team_id: Optional[int],
    new_field_id: Optional[int],
    schedule_entry_id: Optional[int] = None,
    is_deleted: bool = False
) -> int:
    """
    Creates a new event override.
    If schedule_entry_id is None, this override represents a one-off exception.
    Returns the newly created override_id.
    """
    cursor = conn.cursor()
    query = """
    INSERT INTO schedule_entry_overrides 
        (active_schedule_id, schedule_entry_id, override_date, new_start_time, new_end_time, new_team_id, new_field_id, is_deleted)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING override_id;
    """
    try:
        cursor.execute(
            query, 
            (active_schedule_id, schedule_entry_id, override_date, new_start_time, new_end_time, new_team_id, new_field_id, is_deleted)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        print("Database error:", str(e))
        raise e


@with_db_connection
def update_event_override(conn, override_id: int, changes: Dict[str, Any]) -> bool:
    """
    Updates an existing event override with the given changes.
    'changes' is a dict mapping column names to new values.
    Returns True if at least one row was updated.
    """
    if not changes:
        return False

    set_clauses = []
    values = []
    for key, value in changes.items():
        set_clauses.append(f"{key} = %s")
        values.append(value)
    values.append(override_id)
    
    query = f"""
    UPDATE schedule_entry_overrides
    SET {', '.join(set_clauses)}
    WHERE override_id = %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, tuple(values))
    rows_updated = cursor.rowcount > 0
    
    # Commit the transaction
    conn.commit()
    
    return rows_updated


@with_db_connection
def delete_event_override(conn, override_id: int) -> bool:
    """
    Deletes an event override.
    For overrides associated with an existing schedule entry (schedule_entry_id is not null),
    instead of physically deleting, the override is updated to set is_deleted = true.
    For one-off overrides (schedule_entry_id is null), the row is physically deleted.
    Returns True if a row was affected.
    """
    cursor = conn.cursor()
    
    # Determine if this override is linked to an existing schedule entry.
    cursor.execute(
        "SELECT schedule_entry_id FROM schedule_entry_overrides WHERE override_id = %s;",
        (override_id,)
    )
    row = cursor.fetchone()
    if not row:
        return False

    schedule_entry_id = row[0]
    
    if schedule_entry_id is None:
        # One-off override; physically delete the row.
        cursor.execute(
            "DELETE FROM schedule_entry_overrides WHERE override_id = %s;",
            (override_id,)
        )
    else:
        # Override for an existing schedule entry; mark as deleted.
        cursor.execute(
            "UPDATE schedule_entry_overrides SET is_deleted = true WHERE override_id = %s;",
            (override_id,)
        )
    conn.commit()
    return cursor.rowcount > 0
