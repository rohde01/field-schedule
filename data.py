# filename: data.py

def get_teams():
    return [
        # Boys Teams
        {'name': 'U19A', 'year': 'U19'},
        {'name': 'U17A', 'year': 'U17'},
        {'name': 'U15A', 'year': 'U15'},
        {'name': 'U13A', 'year': 'U13'},
        {'name': 'U11A', 'year': 'U11'},
        {'name': 'U10A', 'year': 'U10'},
        
        # Girls Teams
        {'name': 'U19AG', 'year': 'U19-girl'},
        {'name': 'U16AG', 'year': 'U16-girl'},
        {'name': 'U14AG', 'year': 'U14-girl'},
        {'name': 'U13AG', 'year': 'U13-girl'},
    ]

def get_fields():
    """
    Returns a list of field dictionaries with diverse field sizes and subfields.
    """
    return [
        {
            'name': 'K1',
            'size': '11v11',
            'quarter_subfields': [
                {'name': 'K1-1'},
                {'name': 'K1-2'},
                {'name': 'K1-3'},
                {'name': 'K1-4'}
            ],
            'half_subfields': [
                {'name': 'K1-A', 'fields': ['K1-1', 'K1-2']},
                {'name': 'K1-B', 'fields': ['K1-3', 'K1-4']}
            ],
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
            }
        },
        {
            'name': 'G1',
            'size': '8v8',
            'half_subfields': [
                {'name': 'G1-A', 'fields': ['G1-1', 'G1-2']},
                {'name': 'G1-B', 'fields': ['G1-3', 'G1-4']}
            ],
            'availability': {
                'Mon': {'start': '16:00', 'end': '19:00'},
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '19:00'}
            }
        },
        {
            'name': 'G2',
            'size': '5v5',
            'availability': {
                'Mon': {'start': '16:00', 'end': '19:00'},
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '19:00'}
            }
        },
        {
            'name': 'G3',
            'size': '3v3',
            'availability': {
                'Mon': {'start': '16:00', 'end': '19:00'},
                'Tue': {'start': '16:00', 'end': '19:00'},
                'Wed': {'start': '16:00', 'end': '19:00'},
                'Thu': {'start': '16:00', 'end': '19:00'},
                'Fri': {'start': '16:00', 'end': '19:00'}
            }
        }
    ]

def get_5_star_constraints():
    return [
        # U19 - Boys
        {'year': 'U19', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U19', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U17 - Boys
        {'year': 'U17', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U17', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U15 - Boys
        {'year': 'U15', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U15', 'required_size': '8v8', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        {'year': 'U15', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 1, 'length': 4},
        
        # U13 - Boys
        {'year': 'U13', 'required_size': '8v8', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U13', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        
        # U11 - Boys
        {'year': 'U11', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        
        # U10 - Boys
        {'year': 'U10', 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
    ]

# 3-star constraints (girls)
def get_3_star_constraints_girls():
    return [
        # U19-girl
        {'year': 'U19-girl', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U19-girl', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 1, 'length': 4},
        
        # U16-girl
        {'year': 'U16-girl', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 1, 'length': 8},
        {'year': 'U16-girl', 'required_size': '8v8', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U14-girl
        {'year': 'U14-girl', 'required_size': '8v8', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        {'year': 'U14-girl', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
        
        # U13-girl
        {'year': 'U13-girl', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U13-girl', 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 1, 'length': 4},
    ]
