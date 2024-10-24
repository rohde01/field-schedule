def get_teams():
    return [
        # Boys Teams
        {'name': 'U19A', 'year': 'U19'},
        {'name': 'U19A-2', 'year': 'U14'},
        {'name': 'Y15A', 'year': 'U15'},
        {'name': 'U10A', 'year': 'U10'},
        {'name': 'U11A', 'year': 'U11'},
        {'name': 'U13A', 'year': 'U13'},        
         # Girls Teams
        {'name': 'girl', 'year': 'U19-girl'},
        {'name': 'child', 'year': 'U17-girl'},
    ]

def get_fields():
    return [
        {
            'name': 'Kunst 1',
            'size': '11v11',
            'quarter_subfields': [{'name': 'K1-1'}, {'name': 'K1-2'}, {'name': 'K1-3'}, {'name': 'K1-4'}],
            'half_subfields': [{'name': 'K1-A', 'fields': ['K1-1', 'K1-2']}, {'name': 'K1-B', 'fields': ['K1-3', 'K1-4']}],
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'}
            }
        },
        {
            'name': 'G1',
            'size': '8v8',
            'half_subfields': [
                {'name': 'G1-A'},
                {'name': 'G1-B'}
            ],
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'},
            }
        },
        {
            'name': 'Kunst 4',
            'size': '5v5',
            'availability': {
                'Mon': {'start': '16:00', 'end': '18:00'},
                }
        },
    ]

def get_5_star_constraints():
    return [
        # U19 - Boys
        {'year': 'U19', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 1, 'length': 4},

         # U14 - Boys
        {'year': 'U14', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 1, 'length': 6},
        
        # U15 - Boys
        {'year': 'U15', 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 1, 'length': 4},

        # U13 - Boys
        {'year': 'U13', 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 2},
        
        # U10 - Boys
        {'year': 'U10', 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 1, 'length': 4},

        # U11 - Boys
        {'year': 'U11', 'required_size': '8v8', 'subfield_type': 'full', 'sessions': 1, 'length': 4},

        
    ]

def get_3_star_constraints_girls():
    return [
        # U19-girl
        {'year': 'U19-girl', 'required_size': '8v8', 'subfield_type': 'half', 'sessions': 1, 'length': 4},
        # U17-girl
        {'year': 'U17-girl', 'required_size': '8v8', 'subfield_type': 'half', 'sessions': 1, 'length': 4},
    ]
