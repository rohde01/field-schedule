from dataclasses import dataclass
from typing import List, Optional
from database.index import with_db_connection

@dataclass
class Team:
    team_id: int
    name: str
    year: Optional[str]
    club_id: int
    is_active: bool

@with_db_connection
def get_teams(conn, club_id: int, include_inactive: bool = False) -> List[Team]:
    cursor = conn.cursor()
    query = """
    SELECT team_id, name, year, club_id, is_active
    FROM teams
    WHERE club_id = %s
    """
    if not include_inactive:
        query += " AND is_active = true"
    cursor.execute(query, (club_id,))
    return [Team(team_id=row[0], name=row[1], year=row[2], 
                club_id=row[3], is_active=row[4]) 
            for row in cursor.fetchall()]

@with_db_connection
def create_team(conn, team_data: dict) -> Team:
    cursor = conn.cursor()
    query = """
    INSERT INTO teams (name, year, club_id, is_active)
    VALUES (%s, %s, %s, %s)
    RETURNING team_id, name, year, club_id, is_active
    """
    cursor.execute(query, (
        team_data["name"], 
        team_data["year"], 
        team_data["club_id"],
        team_data.get("is_active", True)
    ))
    row = cursor.fetchone()
    conn.commit()
    return Team(team_id=row[0], name=row[1], year=row[2], 
               club_id=row[3], is_active=row[4])

@with_db_connection
def delete_team(conn, team_id: int, hard_delete: bool = False) -> bool:
    cursor = conn.cursor()
    if hard_delete:
        query = "DELETE FROM teams WHERE team_id = %s RETURNING team_id"
    else:
        query = "UPDATE teams SET is_active = false WHERE team_id = %s RETURNING team_id"
    cursor.execute(query, (team_id,))
    deleted = cursor.fetchone() is not None
    conn.commit()
    return deleted