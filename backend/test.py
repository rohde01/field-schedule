# Test module for field conflict detection
from typing import List, Dict
from models.field import Field
from utils import time_str_to_block

def fieldConflicts(schedule: List[Dict], fields: List[Field]) -> None:
    # Build mapping of field_id to Field
    field_map = {f.field_id: f for f in fields}
    # Compute ancestors for each field
    ancestors = {f.field_id: set() for f in fields}
    for f in fields:
        cur = f
        while cur.parent_field_id is not None:
            ancestors[f.field_id].add(cur.parent_field_id)
            cur = field_map[cur.parent_field_id]

    # Convert schedule entries to blocks
    entries = []
    for sess in schedule:
        day = sess['day_of_week']
        s_blk = time_str_to_block(sess['start_time'])
        e_blk = time_str_to_block(sess['end_time'])
        entries.append((sess['session_id'], day, s_blk, e_blk, sess['field_id']))

    # Check each pair for direct conflicts
    for i in range(len(entries)):
        id1, day1, s1, e1, f1 = entries[i]
        for j in range(i+1, len(entries)):
            id2, day2, s2, e2, f2 = entries[j]
            if day1 != day2:
                continue
            if s1 < e2 and s2 < e1:
                # Same field
                if f1 == f2:
                    f_obj = field_map[f1]
                    print(f"Warning: Field '{f_obj.name}' (ID {f1}) is double booked in sessions {id1} and {id2}.")
                # Ancestor-descendant
                elif f1 in ancestors.get(f2, set()):
                    anc = field_map[f1]
                    desc = field_map[f2]
                    print(f"Warning: Cannot schedule {anc.field_type.value} '{anc.name}' (ID {f1}) and its subfield {desc.field_type.value} '{desc.name}' (ID {f2}) at the same time (sessions {id1}, {id2}).")
                elif f2 in ancestors.get(f1, set()):
                    anc = field_map[f2]
                    desc = field_map[f1]
                    print(f"Warning: Cannot schedule {anc.field_type.value} '{anc.name}' (ID {f2}) and its subfield {desc.field_type.value} '{desc.name}' (ID {f1}) at the same time (sessions {id2}, {id1}).")

def analyzeAdjacencyPatterns(schedule: List[Dict]) -> None:
    """
    Analyze the adjacency patterns of teams and count how many have ideal patterns.
    Prints a fraction showing teams with ideal patterns vs total teams.
    
    Ideal patterns:
    - 1 session: always ideal
    - 2 sessions: ideal as long as not back to back
    - 3 sessions: only ideal on mon-wed-fri
    - 4 sessions: only ideal on mon-tue-thu-fri
    """
    # Group sessions by team_id
    team_sessions = {}
    for sess in schedule:
        team_id = sess['team_id']
        if team_id not in team_sessions:
            team_sessions[team_id] = []
        team_sessions[team_id].append(sess)
    
    # Define day order for comparison
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    day_to_num = {day: i for i, day in enumerate(day_order)}
    
    # Define ideal patterns
    ideal_patterns = {
        1: [set()],  # Any single day is ideal
        2: [  # Any non-consecutive pair
            {0, 2}, {0, 3}, {0, 4}, {0, 5}, {0, 6},
            {1, 3}, {1, 4}, {1, 5}, {1, 6},
            {2, 4}, {2, 5}, {2, 6},
            {3, 5}, {3, 6},
            {4, 6}
        ],
        3: [{0, 2, 4}],  # Only mon-wed-fri
        4: [{0, 1, 3, 4}]  # Only mon-tue-thu-fri
    }
    
    ideal_count = 0
    total_teams = len(team_sessions)
    non_ideal_teams = []
    
    for team_id, sessions in team_sessions.items():
        num_sessions = len(sessions)
        
        # Get the days this team has sessions
        team_days = set()
        for sess in sessions:
            day_num = day_to_num.get(sess['day_of_week'])
            if day_num is not None:
                team_days.add(day_num)
        
        # Check if this team has an ideal pattern
        is_ideal = False
        
        if num_sessions == 1:
            # 1 session is always ideal
            is_ideal = True
        elif num_sessions in ideal_patterns:
            # Check if team's days match any ideal pattern for this session count
            for ideal_pattern in ideal_patterns[num_sessions]:
                if team_days == ideal_pattern:
                    is_ideal = True
                    break
        # For session counts not in ideal_patterns (5+), assume not ideal
        
        if is_ideal:
            ideal_count += 1
        else:
            # Convert day numbers back to day names for display
            actual_days = [day_order[d] for d in sorted(team_days)]
            non_ideal_teams.append((team_id, num_sessions, actual_days))
    
    print(f"Adjacency Pattern Analysis: {ideal_count}/{total_teams} teams have ideal patterns")
    
    if non_ideal_teams:
        print("Teams with non-ideal patterns:")
        for team_id, session_count, days in non_ideal_teams:
            print(f"  Team {team_id}: {session_count} sessions on {', '.join(days)}")
    else:
        print("All teams have ideal patterns!")
