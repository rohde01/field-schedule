from dataclasses import dataclass
from typing import List, Optional
from .index import with_db_connection
import psycopg2

@dataclass
class Facility:
    facility_id: int
    club_id: int
    name: str
    is_primary: bool

class FacilityError(Exception):
    """Base exception for facility-related errors"""
    pass

class DuplicatePrimaryFacilityError(FacilityError):
    """Raised when attempting to create a second primary facility"""
    pass

class DuplicateFacilityNameError(FacilityError):
    """Raised when attempting to create a facility with an existing name"""
    pass

def _has_primary_facility(conn, club_id: int) -> bool:
    """Internal function to check if the club already has a primary facility."""
    cursor = conn.cursor()
    query = """
        SELECT EXISTS(
            SELECT 1 FROM facilities 
            WHERE club_id = %s AND is_primary = true
        )
    """
    cursor.execute(query, (club_id,))
    return cursor.fetchone()[0]

@with_db_connection
def get_facilities(conn, club_id: int) -> List[Facility]:
    """Fetches a list of Facility instances from the database for a specific club."""
    cursor = conn.cursor()
    query = """
        SELECT facility_id, club_id, name, is_primary
        FROM facilities
        WHERE club_id = %s
    """
    cursor.execute(query, (club_id,))
    return [
        Facility(
            facility_id=row[0],
            club_id=row[1],
            name=row[2],
            is_primary=row[3]
        )
        for row in cursor.fetchall()
    ]

@with_db_connection
def has_primary_facility(conn, club_id: int) -> bool:
    """Check if the club already has a primary facility."""
    return _has_primary_facility(conn, club_id)

@with_db_connection
def create_facility(conn, club_id: int, name: str, is_primary: bool = False) -> Facility:
    """Creates a new facility in the database."""
    cursor = conn.cursor()
    try:
        if is_primary and _has_primary_facility(conn, club_id):
            raise DuplicatePrimaryFacilityError("Club already has a primary facility")

        print(f"Attempting to create facility: club_id={club_id}, name={name}, is_primary={is_primary}")
        query = """
            INSERT INTO facilities (club_id, name, is_primary)
            VALUES (%s, %s, %s)
            RETURNING facility_id, club_id, name, is_primary
        """
        cursor.execute(query, (club_id, name, is_primary))
        conn.commit()
        
        result = cursor.fetchone()
        return Facility(
            facility_id=result[0],
            club_id=result[1],
            name=result[2],
            is_primary=result[3]
        )
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"Database integrity error: {str(e)}")
        if "unique_club_facility_name" in str(e):
            raise DuplicateFacilityNameError("A facility with this name already exists in this club")
        if "facilities_club_id_fkey" in str(e):
            raise ValueError("Invalid club ID")
        raise FacilityError(str(e))
    except DuplicatePrimaryFacilityError as e:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error creating facility: {str(e)}")
        raise FacilityError(str(e))

@with_db_connection
def get_facility(conn, facility_id: int) -> Optional[Facility]:
    """Fetch a single facility by ID."""
    cursor = conn.cursor()
    query = """
        SELECT facility_id, club_id, name, is_primary
        FROM facilities
        WHERE facility_id = %s
    """
    cursor.execute(query, (facility_id,))
    row = cursor.fetchone()
    if row:
        return Facility(
            facility_id=row[0],
            club_id=row[1],
            name=row[2],
            is_primary=row[3]
        )
    return None