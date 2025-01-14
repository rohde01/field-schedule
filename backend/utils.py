from dataclass import Constraint, Field
from database.teams import get_teams_by_ids
from typing import List

SIZE_TO_CAPACITY = {
    '11v11': 1000,
    '8v8':   500,
    '5v5':   250,
    '3v3':   125,
}

def time_str_to_block(s: str) -> int:
    hh, mm = s.split(':')
    return int(hh)*4 + int(int(mm)//15)

def get_capacity_and_allowed(field: Field) -> tuple[int, List[int], int]:
    total_cap = SIZE_TO_CAPACITY[field.size]
    if field.quarter_subfields:
        max_splits = 4
    elif field.half_subfields:
        max_splits = 2
    else:
        max_splits = 1
    demands = {total_cap}
    if max_splits >= 2:
        demands.add(total_cap // 2)
    if max_splits >= 4:
        demands.add(total_cap // 4)
    allowed_demands = sorted(list(demands))
    return total_cap, allowed_demands, max_splits

def teams_to_constraints(team_ids: List[int]) -> List[Constraint]:
    """Convert a list of team IDs into scheduling constraints."""
    teams = get_teams_by_ids(team_ids)
    constraints_list = []
    
    for team in teams:
        # Use preferred_field_size if available, otherwise use minimum_field_size
        required_size = str(team.preferred_field_size if team.preferred_field_size is not None else team.minimum_field_size)
        # Use training_length if available, otherwise default to 4
        length = team.training_length if team.training_length is not None else 4
        
        constraints_list.append(Constraint(
            team_id=team.team_id,
            sessions=team.weekly_trainings,
            length=length,
            required_size=required_size
        ))
    
    return constraints_list

