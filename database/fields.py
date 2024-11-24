from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .index import with_db_connection
import psycopg2
from database.index import connection_string

@dataclass
class FieldAvailability:
    day_of_week: str
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