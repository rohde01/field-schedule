# filename: data.py

def get_teams():
    return [
        # Boys Teams
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
        {'name': 'U15-3', 'year': 'U15'},
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
         # Girls Teams
        {'name': 'U19A-girl', 'year': 'U19-girl'},
        {'name': 'U16A-girl', 'year': 'U16-girl'},
        {'name': 'U14A-girl', 'year': 'U14-girl'},
        {'name': 'U13A-girl', 'year': 'U13-girl'},
        {'name': 'U16-2-girl', 'year': 'U16-girl'},
        {'name': 'U14-2-girl', 'year': 'U14-girl'},
        {'name': 'U13-2-girl', 'year': 'U13-girl'},
    ]

def get_fields():
    """
    Returns a list of field dictionaries with diverse field sizes and subfields.
    """
    return [
        {
            'name': 'Kunst 1',
            'size': '11v11',
            'quarter_subfields': [{'name': 'K1-1'}, {'name': 'K1-2'}, {'name': 'K1-3'}, {'name': 'K1-4'}],
            'half_subfields': [{'name': 'K1-A', 'fields': ['K1-1', 'K1-2']}, {'name': 'K1-B', 'fields': ['K1-3', 'K1-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
            }
        },
        {
            'name': 'Kunst 2',
            'size': '11v11',
            'quarter_subfields': [{'name': 'K2-1'}, {'name': 'K2-2'}, {'name': 'K2-3'}, {'name': 'K2-4'}],
            'half_subfields': [{'name': 'K2-A', 'fields': ['K2-1', 'K2-2']}, {'name': 'K2-B', 'fields': ['K2-3', 'K2-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
            }
        },
        {
            'name': 'Kunst 3',
            'size': '11v11',
            'quarter_subfields': [{'name': 'K3-1'}, {'name': 'K3-2'}, {'name': 'K3-3'}, {'name': 'K3-4'}],
            'half_subfields': [{'name': 'K3-A', 'fields': ['K3-1', 'K3-2']}, {'name': 'K3-B', 'fields': ['K3-3', 'K3-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
            }
        },
        {
            'name': 'Kunst 4',
            'size': '5v5',
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
            }
        },
        {
            'name': 'Kunst 5',
            'size': '3v3',
            'availability': {
                'Mon': {'start': '16:00', 'end': '20:30'},
                'Tue': {'start': '16:00', 'end': '20:30'},
                'Wed': {'start': '16:00', 'end': '20:30'},
                'Thu': {'start': '16:00', 'end': '20:30'},
                'Fri': {'start': '16:00', 'end': '20:30'}
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
        {'year': 'U15', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'year': 'U15', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U14 - Boys
        {'year': 'U14', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'year': 'U14', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        
        # U13 - Boys
        {'year': 'U13', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'year': 'U13', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U11 - Boys
        {'year': 'U12', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        
        # U11 - Boys
        {'year': 'U11', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        
        # U10 - Boys
        {'year': 'U10', 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
    ]

# 3-star constraints (girls)
def get_3_star_constraints_girls():
    return [
        # U19-girl
        {'year': 'U19-girl', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U19-girl', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U16-girl
        {'year': 'U16-girl', 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'year': 'U16-girl', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U14-girl
        {'year': 'U14-girl', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U14-girl', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        
        # U13-girl
        {'year': 'U13-girl', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U13-girl', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
    ]

