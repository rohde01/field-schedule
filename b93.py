# filename: data.py

def get_teams():
    """Returns a list of team dictionaries with a unique 'team_id' for each team."""
    return [
        # Boys Teams
        {'team_id': 1, 'name': 'U19A', 'year': 'U19'},
        {'team_id': 2, 'name': 'U17A', 'year': 'U17'},
        {'team_id': 3, 'name': 'U19-2', 'year': 'U19'},
        {'team_id': 4, 'name': 'U15A', 'year': 'U15'},
        {'team_id': 5, 'name': 'U14A', 'year': 'U14'},
        {'team_id': 6, 'name': 'U13A', 'year': 'U13'},
        {'team_id': 7, 'name': 'U12A', 'year': 'U12'},
        {'team_id': 8, 'name': 'U17-2', 'year': 'U17'},
        {'team_id': 9, 'name': 'U11A', 'year': 'U11'},
        {'team_id': 10, 'name': 'U10A', 'year': 'U10'},
        {'team_id': 11, 'name': 'U15-2', 'year': 'U15'},
        {'team_id': 12, 'name': 'U15-3', 'year': 'U15'},
        {'team_id': 13, 'name': 'U14-2', 'year': 'U14'},
        {'team_id': 14, 'name': 'U14-3', 'year': 'U14'},
        {'team_id': 15, 'name': 'U13-2', 'year': 'U13'},
        {'team_id': 16, 'name': 'U11-A', 'year': 'U11'},
        {'team_id': 17, 'name': 'U13-3', 'year': 'U13'},
        {'team_id': 18, 'name': 'U12-B', 'year': 'U12'},
        {'team_id': 19, 'name': 'U11-B', 'year': 'U11'},
        {'team_id': 20, 'name': 'U17-3', 'year': 'U17'},
        {'team_id': 21, 'name': 'U15-4', 'year': 'U15'},
        {'team_id': 22, 'name': 'U12-B+', 'year': 'U12'},
        {'team_id': 23, 'name': 'U11-B+', 'year': 'U11'},
        {'team_id': 24, 'name': 'U10-B+', 'year': 'U10'},
        {'team_id': 25, 'name': 'U10-B', 'year': 'U10'},
        {'team_id': 26, 'name': 'U15-5', 'year': 'U15'},
         # Girls Teams
        {'team_id': 27, 'name': 'U19A-girl', 'year': 'U19-girl'},
        {'team_id': 28, 'name': 'U16A-girl', 'year': 'U16-girl'},
        {'team_id': 29, 'name': 'U14A-girl', 'year': 'U14-girl'},
        {'team_id': 30, 'name': 'U13A-girl', 'year': 'U13-girl'},
        {'team_id': 31, 'name': 'U16-2-girl', 'year': 'U16-girl'},
        {'team_id': 32, 'name': 'U14-2-girl', 'year': 'U14-girl'},
        {'team_id': 33, 'name': 'U13-2-girl', 'year': 'U13-girl'},
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

def get_constraints():
    """Returns a list of constraints dictionaries with 'team_id' instead of 'year'."""
    return [
        # U19A Boys (team_id: 1)
        {'team_id': 1, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 1, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U17A Boys (team_id: 2)
        {'team_id': 2, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 2, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U19-2 Boys (team_id: 3)
        {'team_id': 3, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 3, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},

        # U15A Boys (team_id: 4)
        {'team_id': 4, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'team_id': 4, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U14A Boys (team_id: 5)
        {'team_id': 5, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 5, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        
        # U13A Boys (team_id: 6)
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 6, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U12A Boys (team_id: 7)
        {'team_id': 7, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        
        # U17-2 Boys (team_id: 8)
        {'team_id': 8, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 8, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},

        # U11A Boys (team_id: 9)
        {'team_id': 9, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        
        # U10A Boys (team_id: 10)
        {'team_id': 10, 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U15-2 Boys (team_id: 11)
        {'team_id': 11, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'team_id': 11, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U15-3 Boys (team_id: 12)
        {'team_id': 12, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'team_id': 12, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U14-2 Boys (team_id: 13)
        {'team_id': 13, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 13, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U14-3 Boys (team_id: 14)
        {'team_id': 14, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 14, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U13-2 Boys (team_id: 15)
        {'team_id': 15, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 15, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U11-A Boys (team_id: 16)
        {'team_id': 16, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U13-3 Boys (team_id: 17)
        {'team_id': 17, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        {'team_id': 17, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},

        # U12-B Boys (team_id: 18)
        {'team_id': 18, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U11-B Boys (team_id: 19)
        {'team_id': 19, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U17-3 Boys (team_id: 20)
        {'team_id': 20, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 20, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},

        # U15-4 Boys (team_id: 21)
        {'team_id': 21, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'team_id': 21, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U12-B+ Boys (team_id: 22)
        {'team_id': 22, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U11-B+ Boys (team_id: 23)
        {'team_id': 23, 'required_size': '5v5', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U10-B+ Boys (team_id: 24)
        {'team_id': 24, 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U10-B Boys (team_id: 25)
        {'team_id': 25, 'required_size': '3v3', 'subfield_type': 'full', 'sessions': 2, 'length': 4},

        # U15-5 Boys (team_id: 26)
        {'team_id': 26, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 6},
        {'team_id': 26, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 6},

        # U19A Girls (team_id: 27)
        {'team_id': 27, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 27, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U16A Girls (team_id: 28)
        {'team_id': 28, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 28, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},
        
        # U14A Girls (team_id: 29)
        {'team_id': 29, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'team_id': 29, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
        
        # U13A Girls (team_id: 30)
        {'team_id': 30, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'team_id': 30, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},

        # U16-2 Girls (team_id: 31)
        {'team_id': 31, 'required_size': '11v11', 'subfield_type': 'full', 'sessions': 2, 'length': 4},
        {'team_id': 31, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 2, 'length': 4},

        # U14-2 Girls (team_id: 32)
        {'team_id': 32, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'team_id': 32, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},

        # U13-2 Girls (team_id: 33)
        {'team_id': 33, 'required_size': '11v11', 'subfield_type': 'half', 'sessions': 3, 'length': 4},
        {'team_id': 33, 'required_size': '11v11', 'subfield_type': 'quarter', 'sessions': 1, 'length': 4},
    ]
