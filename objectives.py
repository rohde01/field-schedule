# Filename: objectives.py
# Objective functions for the scheduling model.
# Contains functions to add objectives to the CP-SAT model.

from ortools.sat.python import cp_model
from typing import List, Dict, Any
from db import Team


def add_objective_function(
    model: cp_model.CpModel,
    teams: List[Team],
    interval_vars: Dict[int, Any],
    time_slots: Dict[str, List[str]],
    day_name_to_index: Dict[str, int]
) -> None:
    """
    Adds an objective function to the model to minimize penalties for undesirable scheduling patterns
    and slightly discourage scheduling on Fridays.
    """
    CONSECUTIVE_DAY_PENALTY = 100
    PENALTY_PER_DAY_DEVIATION = 400
    FRIDAY_PENALTY = 10

    num_days = len(day_name_to_index)
    penalties = []

    preferred_days = {
        2: [
            [day_name_to_index['Mon'], day_name_to_index['Wed']],
            [day_name_to_index['Tue'], day_name_to_index['Thu']],
            [day_name_to_index['Wed'], day_name_to_index['Fri']]
        ],
        3: [
            [day_name_to_index['Mon'], day_name_to_index['Wed'], day_name_to_index['Fri']]
        ],
        4: [
            [day_name_to_index['Mon'], day_name_to_index['Tue'], day_name_to_index['Thu'], day_name_to_index['Fri']]
        ]
    }

    for team in teams:
        team_id = team.team_id
        if team_id not in interval_vars:
            continue  # Skip teams without interval variables
        team_sessions = [session for sessions in interval_vars[team_id].values() for session in sessions]
        day_vars = [session['day_var'] for session in team_sessions]
        num_sessions = len(day_vars)

        # Penalties for consecutive training days
        for i in range(num_sessions - 1):
            is_consecutive = model.NewBoolVar(f'is_consecutive_{team_id}_{i}')
            model.Add(day_vars[i + 1] == day_vars[i] + 1).OnlyEnforceIf(is_consecutive)
            model.Add(day_vars[i + 1] != day_vars[i] + 1).OnlyEnforceIf(is_consecutive.Not())
            penalty = model.NewIntVar(0, CONSECUTIVE_DAY_PENALTY, f'penalty_consecutive_{team_id}_{i}')
            model.Add(penalty == CONSECUTIVE_DAY_PENALTY * is_consecutive)
            penalties.append(penalty)

        # Preferred pattern matching
        if num_sessions in preferred_days:
            pattern_matches = []
            for pattern in preferred_days[num_sessions]:
                pattern_str = '_'.join(map(str, pattern))
                match = model.NewBoolVar(f'pattern_match_{team_id}_{pattern_str}')
                model.AddAllowedAssignments(day_vars, [pattern]).OnlyEnforceIf(match)
                model.AddForbiddenAssignments(day_vars, [pattern]).OnlyEnforceIf(match.Not())
                pattern_matches.append(match)

            is_matching_any_pattern = model.NewBoolVar(f'is_matching_any_pattern_{team_id}')
            model.AddBoolOr(pattern_matches).OnlyEnforceIf(is_matching_any_pattern)
            model.AddBoolAnd([m.Not() for m in pattern_matches]).OnlyEnforceIf(is_matching_any_pattern.Not())

            pattern_penalty = model.NewIntVar(0, PENALTY_PER_DAY_DEVIATION, f'pattern_penalty_{team_id}')
            model.Add(pattern_penalty == 0).OnlyEnforceIf(is_matching_any_pattern)
            model.Add(pattern_penalty == PENALTY_PER_DAY_DEVIATION).OnlyEnforceIf(is_matching_any_pattern.Not())
            penalties.append(pattern_penalty)
        else:
            # Teams without preferred patterns incur a penalty
            pattern_penalty = model.NewIntVar(0, PENALTY_PER_DAY_DEVIATION, f'pattern_penalty_{team_id}')
            model.Add(pattern_penalty == PENALTY_PER_DAY_DEVIATION)
            penalties.append(pattern_penalty)
            is_matching_any_pattern = model.NewBoolVar(f'is_matching_any_pattern_{team_id}')
            model.Add(is_matching_any_pattern == 0)

        # Friday penalty for all sessions scheduled on Friday
        friday_index = day_name_to_index.get('Fri')
        if friday_index is not None:
            for idx, day_var in enumerate(day_vars):
                is_friday = model.NewBoolVar(f'is_friday_{team_id}_{idx}')
                model.Add(day_var == friday_index).OnlyEnforceIf(is_friday)
                model.Add(day_var != friday_index).OnlyEnforceIf(is_friday.Not())

                friday_penalty = model.NewIntVar(0, FRIDAY_PENALTY, f'friday_penalty_{team_id}_{idx}')
                model.Add(friday_penalty == FRIDAY_PENALTY * is_friday)
                penalties.append(friday_penalty)

    # Minimize total penalties
    total_penalty = sum(penalties)
    model.Minimize(total_penalty)
