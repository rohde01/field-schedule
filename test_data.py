"""
Filename: test_data.py
Test data module for the scheduling problem.

Provides functions to get sample data for teams, fields, and constraints.
"""

def get_teams():
    """Returns a list of team dictionaries with a unique 'team_id' for each team."""
    return [
        {'team_id': 1, 'name': 'U19A', 'year': 'U19'},
        {'team_id': 2, 'name': 'U14A', 'year': 'U14'},
        {'team_id': 3, 'name': 'Y15A', 'year': 'U15'},
        {'team_id': 4, 'name': 'U10A', 'year': 'U10'},
        {'team_id': 5, 'name': 'U11A', 'year': 'U11'},
        {'team_id': 6, 'name': 'U13A', 'year': 'U13'},
        {'team_id': 7, 'name': 'girl', 'year': 'U19-girl'},
        {'team_id': 8, 'name': 'child', 'year': 'U17-girl'},
    ]

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

        {'team_id': 1, 'required_size': '8v8', 'subfield_type': 'quarter', 'sessions': 2, 'length': 4},
        {'team_id': 1, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 3, 'length': 4},

        {'team_id': 2, 'required_cost': 500, 'sessions': 2, 'length': 8},
        {'team_id': 2, 'required_cost': 250, 'sessions': 2, 'length': 6},

        {'team_id': 3, 'required_cost': 500, 'sessions': 1, 'length': 4},
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 2},
        {'team_id': 4, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        {'team_id': 5, 'required_cost': 1000, 'sessions': 1, 'length': 4},

        {'team_id': 7, 'required_cost': 500, 'sessions': 3, 'length': 4},
        {'team_id': 8, 'required_cost': 500, 'sessions': 4, 'length': 4},
    ]
