"""
Filename: test_data.py
Test data module for the scheduling problem.

Provides functions to get sample data for teams, fields, and constraints.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import psycopg2
from collections import defaultdict
from dotenv import load_dotenv
import os
from ortools.sat.python import cp_model

load_dotenv()

connection_string = (
    f"dbname='{os.getenv('DB_NAME')}' user='{os.getenv('DB_USER')}' host='{os.getenv('DB_HOST')}' password='{os.getenv('DB_PASSWORD')}'"
)

@dataclass
class Team:
    team_id: int
    name: str
    year: int

def get_teams() -> List[Team]:
    """Fetches a list of Team instances from the database for a specific club."""
    club_id = 1
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        query = """
        SELECT team_id, name, year
        FROM teams
        WHERE club_id = %s
        """
        cursor.execute(query, (club_id,))
        teams = [Team(*row) for row in cursor.fetchall()]
        return teams
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

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

def get_fields() -> List[Field]:
    """Fetches a list of Field instances from the database for a specific facility."""
    facility_id = 1
    try:
        conn = psycopg2.connect(connection_string)
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

            # Remove duplicate quarter subfields
            unique_quarters = {field.field_id: field for field in full_field.quarter_subfields}
            full_field.quarter_subfields = list(unique_quarters.values())

            field_list.append(full_field)

        return field_list

    except Exception as e:
        print(f"Error fetching fields: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@dataclass
class Constraint:
    team_id: int
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    sessions: int = 0
    length: int = 0
    partial_ses_space: Optional[str] = None
    partial_ses_time: Optional[int] = None
    start_time: Optional[str] = None 

def get_constraints() -> List[Constraint]:
    """Returns a list of Constraint instances with 'team_id' instead of 'year'."""
    constraints_data = [
        {'team_id': 2, 'required_cost': 250, 'sessions': 3, 'length': 4,
         'partial_ses_space': 500, 'partial_ses_time': 2},
        
        {'team_id': 3, 'required_cost': 500, 'sessions': 1, 'length': 4, 'start_time': '16:15'},
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 2},
        {'team_id': 4, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        {'team_id': 5, 'required_cost': 1000, 'sessions': 1, 'length': 4},
        {'team_id': 7, 'required_cost': 500, 'sessions': 3, 'length': 4},
        {'team_id': 8, 'required_cost': 500, 'sessions': 4, 'length': 4},
        {'team_id': 9, 'required_cost': 500, 'sessions': 4, 'length': 4},
    ]
    return [Constraint(**data) for data in constraints_data]

def save_schedule(
    solver: cp_model.CpSolver,
    teams: List[Team],
    interval_vars: Dict[int, Any],
    field_name_to_id: Dict[str, int],
    club_id: int = 1
) -> None:
    """
    Saves the generated schedule into the 'schedules' and 'schedule_entries' tables.
    """
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # Insert a new schedule into the schedules table
        schedule_name = "Generated Schedule"
        insert_schedule_query = """
        INSERT INTO schedules (club_id, name)
        VALUES (%s, %s)
        RETURNING schedule_id;
        """
        cursor.execute(insert_schedule_query, (club_id, schedule_name))
        schedule_id = cursor.fetchone()[0]

        schedule_entries = []
        for team in teams:
            team_id = team.team_id
            if team_id not in interval_vars:
                continue
            for idx_constraint in interval_vars[team_id]:
                sessions = interval_vars[team_id][idx_constraint]
                for session in sessions:
                    parent_schedule_entry_id = None
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

        insert_entries_query = """
        INSERT INTO schedule_entries (schedule_id, team_id, field_id, session_start, session_end)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_entries_query, schedule_entries)
        conn.commit()

    except Exception as e:
        print(f"Error saving schedule: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_schedule_entries(schedule_id: int) -> List[tuple]:
    """Fetches schedule entries from the database for the given schedule_id."""
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        query = """
        SELECT se.team_id, se.field_id, se.session_start, se.session_end, se.parent_schedule_entry_id
        FROM schedule_entries se
        WHERE se.schedule_id = %s
        """
        cursor.execute(query, (schedule_id,))
        entries = cursor.fetchall()
        return entries
    except Exception as e:
        print(f"Error fetching schedule entries: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()