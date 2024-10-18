def get_fields():
    return [
        {
            'name': 'Græs 1',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G1-1', 'G1-2', 'G1-3', 'G1-4'],
            'availability': {
                'Mon': {'start': '16:00', 'end': '21:00'},
                'Tue': {'start': '16:00', 'end': '21:00'},
                'Wed': {'start': '16:00', 'end': '21:00'},
                'Thu': {'start': '16:00', 'end': '21:00'},
                'Fri': {'start': '16:00', 'end': '21:00'},
            }
        },

        {
            'name': 'Græs 2',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G2-1', 'G2-2', 'G2-3', 'G2-4'],
            'availability': {
                'Mon': {'start': '16:00', 'end': '21:00'},
                'Tue': {'start': '16:00', 'end': '21:00'},
                'Wed': {'start': '16:00', 'end': '21:00'},
                'Thu': {'start': '16:00', 'end': '21:00'},
                'Fri': {'start': '16:00', 'end': '21:00'},
            }
        },
        
    ]


def get_teams():
    return [
        {'name': 'U19A', 'level': 'academy', 'gender': 'boys', 'year': 'U19'},
        {'name': 'U17A', 'level': 'academy', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U19-2', 'level': 'youth', 'gender': 'boys', 'year': 'U19'},
        {'name': 'U19A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U19-girl'},
        {'name': 'U15A', 'level': 'academy', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U14A', 'level': 'academy', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U13A', 'level': 'academy', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U14A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U14-girl'},
        {'name': 'U13A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U13-girl'},
        {'name': 'U16A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U16-girl'},
        {'name': 'U12A', 'level': 'academy', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U17-2', 'level': 'youth', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U11A', 'level': 'academy', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U10A', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U15-2', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U15-3', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U14-2', 'level': 'youth', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U14-3', 'level': 'youth', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U13-2', 'level': 'youth', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U11-A', 'level': 'child', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U13-3', 'level': 'youth', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U12-B', 'level': 'youth', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U11-B', 'level': 'youth', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U17-3', 'level': 'youth', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U15-4', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U12-B+', 'level': 'youth', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U11-B+', 'level': 'youth', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U10-B+', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U16-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U16-girl'},
        {'name': 'U14-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U14-girl'},
        {'name': 'U13-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U13-girl'},
        {'name': 'U10-B', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U15-5', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
    ]