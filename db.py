"""
Filename: test_data.py
Test data module for the scheduling problem.

Provides functions to get sample data for teams, fields, and constraints.
"""

import pyodbc
from collections import defaultdict

connection_string = (
    "DRIVER=SQL Server;"
    "SERVER=SRV9DNBDBM078;"
    "DATABASE=workspace01;"
    "Trusted_Connection=Yes;"
)

def get_teams():
    """Fetches a list of team dictionaries from the database for a specific club."""

    club_id = 1

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
        SELECT team_id, name, year
        FROM area116.teams
        WHERE club_id = ?
        """

        cursor.execute(query, club_id)
        columns = [column[0] for column in cursor.description]
        teams = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return teams
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def get_fields():
    """Fetches a list of field dictionaries from the database for a specific facility."""

    facility_id = 1

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        fields_query = """
        SELECT f.field_id, f.name, f.size, f.field_type, f.parent_field_id,
               fa.day_of_week, fa.start_time, fa.end_time
        FROM area116.fields f
        LEFT JOIN area116.field_availability fa ON f.field_id = fa.field_id
        WHERE f.facility_id = ?
        """
        cursor.execute(fields_query, facility_id)
        rows = cursor.fetchall()
        fields_by_id = {}
        parent_to_children = {}

        for row in rows:
            field_id = row.field_id
            if field_id not in fields_by_id:
                fields_by_id[field_id] = {
                    'field_id': field_id,
                    'name': row.name,
                    'size': row.size,
                    'field_type': row.field_type,
                    'parent_field_id': row.parent_field_id,
                    'availability': {}
                }
                parent_id = row.parent_field_id
                if parent_id:
                    parent_to_children.setdefault(parent_id, []).append(fields_by_id[field_id])
            if row.day_of_week is not None:
                day_of_week = row.day_of_week
                start_time = str(row.start_time)[:5]
                end_time = str(row.end_time)[:5]
                fields_by_id[field_id]['availability'].setdefault(day_of_week, {'start': start_time, 'end': end_time})
        full_fields = [field for field in fields_by_id.values() if field['field_type'] == 'full']
        field_list = []
        for full_field in full_fields:
            field_dict = {
                'name': full_field['name'],
                'size': full_field['size'],
                'quarter_subfields': [],
                'half_subfields': [],
                'availability': full_field['availability']
            }
            children = parent_to_children.get(full_field['field_id'], [])
            half_fields = [child for child in children if child['field_type'] == 'half']
            quarter_fields_direct = [child for child in children if child['field_type'] == 'quarter']

            for qf in quarter_fields_direct:
                field_dict['quarter_subfields'].append({'name': qf['name']})

            for half_field in half_fields:
                quarter_children = parent_to_children.get(half_field['field_id'], [])
                quarter_names = [child['name'] for child in quarter_children if child['field_type'] == 'quarter']
                field_dict['half_subfields'].append({'name': half_field['name'], 'fields': quarter_names})
                for qf_name in quarter_names:
                    field_dict['quarter_subfields'].append({'name': qf_name})

            unique_quarters = {tuple(subfield.items()) for subfield in field_dict['quarter_subfields']}
            field_dict['quarter_subfields'] = [dict(t) for t in unique_quarters]

            field_list.append(field_dict)

        return field_list

    except Exception as e:
        print(f"Error fetching fields: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def get_constraints():
    """Returns a list of constraints dictionaries with 'team_id' instead of 'year'."""
    return [
        {'team_id': 1, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4,
        'partial_ses_space': 'full', 'partial_ses_time': 4},

        {'team_id': 2, 'required_cost': 250, 'sessions': 3, 'length': 4,
         'partial_ses_space': 500, 'partial_ses_time': 2},

        {'team_id': 3, 'required_cost': 500, 'sessions': 1, 'length': 4},
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 2},
        {'team_id': 4, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        {'team_id': 5, 'required_cost': 1000, 'sessions': 1, 'length': 4},

        {'team_id': 7, 'required_cost': 500, 'sessions': 3, 'length': 4},
        {'team_id': 8, 'required_cost': 500, 'sessions': 4, 'length': 4},
    ]
