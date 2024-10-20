def get_teams():
    """
    Returns a list of team dictionaries.
    """
    return [
        {'name': 'U19A', 'year': 'U19'},
        {'name': 'U15A', 'year': 'U15'},
        {'name': 'U14A', 'year': 'U14'},
        {'name': 'U12A', 'year': 'U12'},
        {'name': 'U11A', 'year': 'U11'},
        {'name': 'U10A', 'year': 'U10'},
    ]
pass

def get_fields():
    """
    Returns a list of field dictionaries.
    """
    return [
        {
            'name': 'Græs 1',
            'size': 'full',
            'quarter_subfields': ['G1-1', 'G1-2', 'G1-3', 'G1-4'],
            'half_subfields': [
                ['G1-1', 'G1-2'],
                ['G1-3', 'G1-4']
            ],
            'availability': {
                'Fri': {'start': '16:00', 'end': '19:00'},
                'Sat': {'start': '16:00', 'end': '19:00'},
                'Sun': {'start': '16:00', 'end': '19:00'},
            }
        },
        {
            'name': 'Græs 2',
            'size': 'full',
            'quarter_subfields': ['G2-1', 'G2-2', 'G2-3', 'G2-4'],
            'half_subfields': [
                ['G2-1', 'G2-2'],
                ['G2-3', 'G2-4']
            ],
            'availability': {
                'Fri': {'start': '16:00', 'end': '19:00'},
                'Sat': {'start': '16:00', 'end': '19:00'},
                'Sun': {'start': '16:00', 'end': '19:00'},
            }
        },
        {
            'name': 'Græs 3',
            'size': 'full',
            'quarter_subfields': ['G3-1', 'G3-2', 'G3-3', 'G3-4'],
            'half_subfields': [
                ['G3-1', 'G3-2'],
                ['G3-3', 'G3-4']
            ],
            'availability': {
                'Fri': {'start': '16:00', 'end': '19:00'},
                'Sat': {'start': '16:00', 'end': '19:00'},
                'Sun': {'start': '16:00', 'end': '19:00'},
            }
        },
    ]
pass

def get_constraints():
    """
    Returns a list of constraint dictionaries.
    """
    return [
        {'year': 'U19', 'required_size': 'half', 'sessions': 3, 'length': 8},
        {'year': 'U15', 'required_size': 'half', 'sessions': 3, 'length': 5},
        {'year': 'U14', 'required_size': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U12', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        {'year': 'U11', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        {'year': 'U10', 'required_size': 'half', 'sessions': 1, 'length': 2},
    ]
pass