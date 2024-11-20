"""
Filename: test_data.py
Test data module for the scheduling problem.

Provides functions to get sample data for teams, fields, and constraints.
"""

import pyodbc

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
        
        teams = [
            {'team_id': row.team_id, 'name': row.name, 'year': row.year}
            for row in cursor.fetchall()
        ]
        
        return teams
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def get_fields():
    """Returns a list of field dictionaries."""
    return [
        {
            'name': 'Kunst 1',
            'size': '11v11',
            'quarter_subfields': [{'name': 'K1-1'}, {'name': 'K1-2'}, {'name': 'K1-3'}, {'name': 'K1-4'}],
            'half_subfields': [{'name': 'K1-A', 'fields': ['K1-1', 'K1-2']}, {'name': 'K1-B', 'fields': ['K1-3', 'K1-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'},
                'Tue': {'start': '16:00', 'end': '18:00'},
                'Wed': {'start': '16:00', 'end': '18:00'},
                'Thu': {'start': '16:00', 'end': '18:00'},
                'Fri': {'start': '16:00', 'end': '18:00'}
            }
        },
        {
            'name': 'G1',
            'size': '8v8',
            'quarter_subfields': [{'name': 'G1-1'}, {'name': 'G1-2'}, {'name': 'G1-3'}, {'name': 'G1-4'}],
            'half_subfields': [{'name': 'G1-A', 'fields': ['G1-1', 'G1-2']}, {'name': 'G1-B', 'fields': ['G1-3', 'G1-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'},
                'Tue': {'start': '16:00', 'end': '18:00'},
                'Wed': {'start': '16:00', 'end': '18:00'},
                'Thu': {'start': '16:00', 'end': '18:00'},
                'Fri': {'start': '16:00', 'end': '18:00'}
            }
        },
        {
            'name': 'Kunst 4',
            'size': '5v5',
            'half_subfields': [{'name': 'K4-A'}, {'name': 'K4-B'}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'},
                'Tue': {'start': '16:00', 'end': '18:00'},
                'Wed': {'start': '16:00', 'end': '18:00'},
                'Thu': {'start': '16:00', 'end': '18:00'},
                'Fri': {'start': '16:00', 'end': '18:00'}
            }
        },
    ]

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
