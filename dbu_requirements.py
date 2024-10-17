# 5-star constraints
def get_5_star_constraints():
    return [
        {'year': 'U19', 'required_size': 'full', 'sessions': 2},
        {'year': 'U17', 'required_size': 'full', 'sessions': 2},
        {'year': 'U15', 'required_size': 'full', 'sessions': 1}, {'year': 'U15', 'required_size': 'half', 'sessions': 1},
        {'year': 'U14', 'required_size': 'half', 'sessions': 3},
        {'year': 'U13', 'required_size': 'half', 'sessions': 3},
        {'year': 'U10', 'required_size': 'quarter', 'sessions': 2},
        {'year': 'U11', 'required_size': 'quarter', 'sessions': 2},
        {'year': 'U12', 'required_size': 'quarter', 'sessions': 2},
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 3},
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 3},
        {'year': 'U16-girl', 'required_size': 'full', 'sessions': 2},
        {'year': 'U19-girl', 'required_size': 'full', 'sessions': 2},
    ]

# 4-star constraints
def get_4_star_constraints():
    return {
        'U19': {'required_size': 'full', 'sessions': 1},
        'U17': {'required_size': 'full', 'sessions': 1},
        'U15': {'required_size': 'full', 'sessions': 0},
        'U14': {'required_size': 'half', 'sessions': 2},
        'U13': {'required_size': 'half', 'sessions': 2},
        'U10': {'required_size': 'quarter', 'sessions': 1},
        'U11': {'required_size': 'quarter', 'sessions': 1},
        'U12': {'required_size': 'quarter', 'sessions': 1},
        'U13-girl': {'required_size': 'half', 'sessions': 2},
        'U14-girl': {'required_size': 'half', 'sessions': 2},
        'U16-girl': {'required_size': 'full', 'sessions': 1},
        'U19-girl': {'required_size': 'full', 'sessions': 1},
    }
