def get_5_star_constraints():
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

def get_3_star_constraints_girls():
    return [
        #U19-girl
        {'year': 'U19-girl', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U19-girl', 'required_size': 'half', 'sessions': 3, 'length': 4},
        #U16-girl
        {'year': 'U16-girl', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U16-girl', 'required_size': 'half', 'sessions': 3, 'length': 4},
        #U14-girl
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U13-girl
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 3, 'length': 4},
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
    ]