# filename: data.py

def get_teams():
    return [
        {'name': 'U19A', 'year': 'U19'},
        {'name': 'U17A', 'year': 'U17'},
        {'name': 'U19-2', 'year': 'U19'},
        {'name': 'U15A', 'year': 'U15'},
        {'name': 'U14A', 'year': 'U14'},
        {'name': 'U13A', 'year': 'U13'},
        {'name': 'U12A', 'year': 'U12'},
        {'name': 'U17-2', 'year': 'U17'},
        {'name': 'U11A', 'year': 'U11'},
        {'name': 'U10A', 'year': 'U10'},
        {'name': 'U15-2', 'year': 'U15'},
        {'name': 'YYY', 'year': 'U15'},
        {'name': 'U14-2', 'year': 'U14'},
        {'name': 'U14-3', 'year': 'U14'},
        {'name': 'U13-2', 'year': 'U13'},
        {'name': 'U11-A', 'year': 'U11'},
        {'name': 'U13-3', 'year': 'U13'},
        {'name': 'U12-B', 'year': 'U12'},
        {'name': 'U11-B', 'year': 'U11'},
        {'name': 'U17-3', 'year': 'U17'},
        {'name': 'U15-4', 'year': 'U15'},
        {'name': 'U12-B+', 'year': 'U12'},
        {'name': 'U11-B+', 'year': 'U11'},
        {'name': 'U10-B+', 'year': 'U10'},
        {'name': 'U10-B', 'year': 'U10'},
        {'name': 'U15-5', 'year': 'U15'},
    ]

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
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '23:15'},
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
                'Mon': {'start': '16:00', 'end': '19:00'},
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '19:00'},
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
                'Mon': {'start': '16:00', 'end': '19:00'},
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '19:00'},
            }
        },
    ]
pass

def get_constraints():
    return [
        #U19
        {'year': 'U19', 'required_size': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U19', 'required_size': 'half', 'sessions': 2, 'length': 4},
        #U17
        {'year': 'U17', 'required_size': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U17', 'required_size': 'half', 'sessions': 2, 'length': 4},
        #U15
        {'year': 'U15', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U15', 'required_size': 'half', 'sessions': 2, 'length': 4},
        {'year': 'U15', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U14
        {'year': 'U14', 'required_size': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U14', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U13
        {'year': 'U13', 'required_size': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U13', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U12
        {'year': 'U12', 'required_size': 'quarter', 'sessions': 2, 'length': 4},
        #U11
        {'year': 'U11', 'required_size': 'quarter', 'sessions': 2, 'length': 4},
        #U10
        {'year': 'U10', 'required_size': 'quarter', 'sessions': 2, 'length': 4},
    ]

