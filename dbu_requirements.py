# 5-star constraints
def get_5_star_constraints():
    return {
        'U19': {'required_size': 'full', 'sessions': 2},
        'U17': {'required_size': 'full', 'sessions': 2},
        'U15': {'required_size': 'full', 'sessions': 1},
        'U14': {'required_size': 'half', 'sessions': 3},
        'U13': {'required_size': 'half', 'sessions': 3},
        'U10': {'required_size': 'quarter', 'sessions': 2},
        'U11': {'required_size': 'quarter', 'sessions': 2},
        'U12': {'required_size': 'quarter', 'sessions': 2},
        'U13-girl': {'required_size': 'half', 'sessions': 3},
        'U14-girl': {'required_size': 'half', 'sessions': 3},
        'U16-girl': {'required_size': 'full', 'sessions': 2},
        'U19-girl': {'required_size': 'full', 'sessions': 2},
    }

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
