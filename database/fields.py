from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from .index import with_db_connection
import psycopg2
from database.index import connection_string

@dataclass
class FieldAvailability:
    day_of_week: Literal['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_time: str 
    end_time: str    

@dataclass
class Field:
    field_id: int
    name: str
    size: str
    field_type: str
    parent_field_id: Optional[int]
    availability: Dict[str, FieldAvailability] = field(default_factory=dict)
    quarter_subfields: List['Field'] = field(default_factory=list)
    half_subfields: List['Field'] = field(default_factory=list)

@with_db_connection
def get_fields(conn, facility_id: int) -> List[Field]:
    """Fetches a list of Field instances from the database for a specific facility."""
    cursor = conn.cursor()
    fields_query = """
        SELECT f.field_id, f.name, f.size, f.field_type, f.parent_field_id,
            fa.day_of_week, fa.start_time, fa.end_time
        FROM fields f
        LEFT JOIN field_availability fa ON f.field_id = fa.field_id
        WHERE f.facility_id = %s
        """
    cursor.execute(fields_query, (facility_id,))
    rows = cursor.fetchall()
    fields_by_id: Dict[int, Field] = {}
    parent_to_children: Dict[int, List[Field]] = {}

    for row in rows:
        field_id = row[0]
        if field_id not in fields_by_id:
            fields_by_id[field_id] = Field(
                field_id=field_id,
                name=row[1],
                size=row[2],
                field_type=row[3],
                parent_field_id=row[4],
                availability={}
            )
            parent_id = row[4]
            if parent_id:
                parent_to_children.setdefault(parent_id, []).append(fields_by_id[field_id])

        if row[5] is not None:
            day_of_week = row[5]
            start_time = str(row[6])[:5]
            end_time = str(row[7])[:5]
            fields_by_id[field_id].availability[day_of_week] = FieldAvailability(
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

    full_fields = [field for field in fields_by_id.values() if field.field_type == 'full']
    field_list: List[Field] = []
    for full_field in full_fields:
        children = parent_to_children.get(full_field.field_id, [])
        half_fields = [child for child in children if child.field_type == 'half']
        quarter_fields_direct = [child for child in children if child.field_type == 'quarter']

        full_field.quarter_subfields.extend(quarter_fields_direct)

        for half_field in half_fields:
            quarter_children = parent_to_children.get(half_field.field_id, [])
            half_field.quarter_subfields.extend(quarter_children)
            full_field.half_subfields.append(half_field)
            full_field.quarter_subfields.extend(quarter_children)
            
        unique_quarters = {field.field_id: field for field in full_field.quarter_subfields}
        full_field.quarter_subfields = list(unique_quarters.values())

        field_list.append(full_field)

    return field_list

@with_db_connection
def create_field(conn, facility_id: int, name: str, size: str, field_type: str, parent_field_id: Optional[int] = None) -> Field:
    """Creates a new field in the database."""
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO fields (facility_id, name, size, field_type, parent_field_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING field_id, name, size, field_type, parent_field_id
        """
        cursor.execute(query, (facility_id, name, size, field_type, parent_field_id))
        conn.commit()
        
        result = cursor.fetchone()
        return Field(
            field_id=result[0],
            name=result[1],
            size=result[2],
            field_type=result[3],
            parent_field_id=result[4]
        )
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "fields_facility_id_name_key" in str(e):
            raise ValueError("A field with this name already exists in this facility")
        if "fields_parent_field_id_fkey" in str(e):
            raise ValueError("Invalid parent field ID")
        if "fields_facility_id_fkey" in str(e):
            raise ValueError("Invalid facility ID")
        raise

@with_db_connection
def add_field_availabilities(conn, field_id: int, availabilities: List[FieldAvailability]) -> int:
    cursor = conn.cursor()
    added = 0
    try:
        for avail in availabilities:
            query = """
                INSERT INTO field_availability (field_id, day_of_week, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                field_id,
                avail.day_of_week,
                avail.start_time,
                avail.end_time
            ))
            added += 1
        conn.commit()
        return added
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "field_availability_pkey" in str(e):
            raise ValueError("Availability already exists for this time slot")
        raise

@with_db_connection
def delete_field(conn, field_id: int) -> dict:
    """Deletes a field and its child fields based on usage in schedule entries."""
    cursor = conn.cursor()
    
    try:
        # Check if field exists and get all related field IDs (including children)
        cursor.execute("""
            WITH RECURSIVE field_tree AS (
                SELECT field_id FROM fields WHERE field_id = %s
                UNION
                SELECT f.field_id FROM fields f
                INNER JOIN field_tree ft ON f.parent_field_id = ft.field_id
            )
            SELECT array_agg(field_id) FROM field_tree
        """, (field_id,))
        
        field_ids = cursor.fetchone()[0]
        if not field_ids:
            raise ValueError("Field not found")

        # Check if any of these fields are used in schedule entries
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM schedule_entries 
                WHERE field_id = ANY(%s)
            )
        """, (field_ids,))
        
        has_schedules = cursor.fetchone()[0]

        if has_schedules:
            # Soft delete - update is_active flag
            cursor.execute("""
                UPDATE fields 
                SET is_active = false 
                WHERE field_id = ANY(%s)
            """, (field_ids,))
        else:
            # Hard delete - field_availability will be deleted automatically due to CASCADE
            cursor.execute("""
                DELETE FROM fields 
                WHERE field_id = ANY(%s)
            """, (field_ids,))

        conn.commit()
        return {
            "success": True,
            "action": "soft_delete" if has_schedules else "hard_delete",
            "affected_fields": len(field_ids)
        }
        
    except Exception as e:
        conn.rollback()
        raise