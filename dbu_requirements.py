# 5-star constraints
def get_5_star_constraints():
    return [
        #U19
        {'year': 'U19', 'required_size': 'full', 'sessions': 2},
        {'year': 'U19', 'required_size': 'half', 'sessions': 2},
        #U17
        {'year': 'U17', 'required_size': 'full', 'sessions': 2},
        {'year': 'U17', 'required_size': 'half', 'sessions': 2},
        #U15
        {'year': 'U15', 'required_size': 'full', 'sessions': 1}, 
        {'year': 'U15', 'required_size': 'half', 'sessions': 2}, 
        {'year': 'U15', 'required_size': 'quarter', 'sessions': 1},
        #U14
        {'year': 'U14', 'required_size': 'half', 'sessions': 3}, 
        {'year': 'U14', 'required_size': 'quarter', 'sessions': 1},
        #U13
        {'year': 'U13', 'required_size': 'half', 'sessions': 3}, 
        {'year': 'U13', 'required_size': 'quarter', 'sessions': 1},
        #U12
        {'year': 'U12', 'required_size': 'quarter', 'sessions': 2},
        #U11
        {'year': 'U11', 'required_size': 'quarter', 'sessions': 2},
        #U10
        {'year': 'U10', 'required_size': 'quarter', 'sessions': 2},
    ]

# 3-star constraints (girls)
def get_3_star_constraints_girls():
    return [
        #U19-girl
        {'year': 'U19-girl', 'required_size': 'full', 'sessions': 1},
        {'year': 'U19-girl', 'required_size': 'half', 'sessions': 3},
        #U16-girl
        {'year': 'U16-girl', 'required_size': 'full', 'sessions': 1},
        {'year': 'U16-girl', 'required_size': 'half', 'sessions': 3},
        #U14-girl
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 3},
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 1},
        #U13-girl
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 3},
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 1},
    ]