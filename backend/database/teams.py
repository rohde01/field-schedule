from dataclasses import dataclass
from typing import List, Optional
from database.index import with_db_connection

@dataclass
class Team:
    team_id: int
    name: str
    year: str
    club_id: int
    gender: str
    is_academy: bool
    minimum_field_size: int
    preferred_field_size: Optional[int]
    level: int
    is_active: bool
    weekly_trainings: int

@with_db_connection
def get_teams(conn, club_id: int, include_inactive: bool = True) -> List[Team]:
    cursor = conn.cursor()
    query = """
    SELECT team_id, name, year, club_id, gender, is_academy, 
           minimum_field_size, preferred_field_size, level, is_active, weekly_trainings
    FROM teams
    WHERE club_id = %s
    """
    if not include_inactive:
        query += " AND is_active = true"
    cursor.execute(query, (club_id,))
    return [Team(*row) for row in cursor.fetchall()]

@with_db_connection
def create_team(conn, team_data: dict) -> Team:
    cursor = conn.cursor()
    query = """
    INSERT INTO teams (name, year, club_id, gender, is_academy, 
                      minimum_field_size, preferred_field_size, level, is_active, weekly_trainings)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING team_id, name, year, club_id, gender, is_academy, 
              minimum_field_size, preferred_field_size, level, is_active, weekly_trainings
    """
    cursor.execute(query, (
        team_data["name"],
        team_data["year"],
        team_data["club_id"],
        team_data["gender"],
        team_data["is_academy"],
        team_data["minimum_field_size"],
        team_data.get("preferred_field_size"),
        team_data["level"],
        team_data.get("is_active", True),
        team_data["weekly_trainings"]
    ))
    row = cursor.fetchone()
    conn.commit()
    return Team(*row)

@with_db_connection
def delete_team(conn, team_id: int) -> dict:
    cursor = conn.cursor()
    
    # Check for references in schedule_entries
    check_query = """
    SELECT EXISTS(
        SELECT 1 FROM schedule_entries 
        WHERE team_id = %s
    )
    """
    cursor.execute(check_query, (team_id,))
    has_schedules = cursor.fetchone()[0]
    
    if has_schedules:
        # Soft delete if team has schedule entries
        query = """
        UPDATE teams 
        SET is_active = false 
        WHERE team_id = %s 
        RETURNING team_id
        """
        cursor.execute(query, (team_id,))
        success = cursor.fetchone() is not None
        action = "soft_deleted"
    else:
        # Hard delete if no schedule entries exist
        query = """
        DELETE FROM teams 
        WHERE team_id = %s 
        RETURNING team_id
        """
        cursor.execute(query, (team_id,))
        success = cursor.fetchone() is not None
        action = "hard_deleted"
    
    conn.commit()
    return {"success": success, "action": action}

@with_db_connection
def get_teams_by_ids(conn, team_ids: List[int]) -> List[Team]:
    cursor = conn.cursor()
    format_strings = ','.join(['%s'] * len(team_ids))
    query = f"""
    SELECT team_id, name, year, club_id, gender, is_academy, 
           minimum_field_size, preferred_field_size, level, is_active, weekly_trainings
    FROM teams
    WHERE team_id IN ({format_strings})
    """
    cursor.execute(query, tuple(team_ids))
    return [Team(*row) for row in cursor.fetchall()]

@with_db_connection
def update_team(conn, team_id: int, update_data: dict) -> Optional[Team]:
    if not update_data:
        return None
        
    cursor = conn.cursor()
    
    # Construct dynamic UPDATE query
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"""
    UPDATE teams 
    SET {set_clause}
    WHERE team_id = %s
    RETURNING team_id, name, year, club_id, gender, is_academy, 
              minimum_field_size, preferred_field_size, level, is_active, weekly_trainings
    """
    
    # Execute query with update values plus team_id
    cursor.execute(query, list(update_data.values()) + [team_id])
    row = cursor.fetchone()
    
    if not row:
        return None
        
    conn.commit()
    return Team(*row)
