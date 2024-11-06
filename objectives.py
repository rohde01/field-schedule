from ortools.sat.python import cp_model


def add_objective_function(model, teams, interval_vars, time_slots, day_name_to_index):
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
        team_name = team['name']
        team_sessions = [session for sessions in interval_vars[team_name].values() for session in sessions]
        day_vars = [session['day_var'] for session in team_sessions]
        num_sessions = len(day_vars)

        # Penalties for consecutive training days
        for i in range(num_sessions - 1):
            is_consecutive = model.NewBoolVar(f'is_consecutive_{team_name}_{i}')
            model.Add(day_vars[i + 1] == day_vars[i] + 1).OnlyEnforceIf(is_consecutive)
            model.Add(day_vars[i + 1] != day_vars[i] + 1).OnlyEnforceIf(is_consecutive.Not())
            penalty = model.NewIntVar(0, CONSECUTIVE_DAY_PENALTY, f'penalty_consecutive_{team_name}_{i}')
            model.Add(penalty == CONSECUTIVE_DAY_PENALTY * is_consecutive)
            penalties.append(penalty)

        # Preferred pattern matching
        if num_sessions in preferred_days:
            pattern_matches = []
            for pattern in preferred_days[num_sessions]:
                match = model.NewBoolVar(f'pattern_match_{team_name}_{"_".join(map(str, pattern))}')
                model.AddAllowedAssignments(day_vars, [pattern]).OnlyEnforceIf(match)
                model.AddForbiddenAssignments(day_vars, [pattern]).OnlyEnforceIf(match.Not())
                pattern_matches.append(match)

            is_matching_any_pattern = model.NewBoolVar(f'is_matching_any_pattern_{team_name}')
            model.AddBoolOr(pattern_matches).OnlyEnforceIf(is_matching_any_pattern)
            model.AddBoolAnd([m.Not() for m in pattern_matches]).OnlyEnforceIf(is_matching_any_pattern.Not())

            pattern_penalty = model.NewIntVar(0, PENALTY_PER_DAY_DEVIATION, f'pattern_penalty_{team_name}')
            model.Add(pattern_penalty == 0).OnlyEnforceIf(is_matching_any_pattern)
            model.Add(pattern_penalty == PENALTY_PER_DAY_DEVIATION).OnlyEnforceIf(is_matching_any_pattern.Not())
            penalties.append(pattern_penalty)
        else:
            # Teams without preferred patterns incur a penalty
            pattern_penalty = model.NewIntVar(0, PENALTY_PER_DAY_DEVIATION, f'pattern_penalty_{team_name}')
            model.Add(pattern_penalty == PENALTY_PER_DAY_DEVIATION)
            penalties.append(pattern_penalty)
            is_matching_any_pattern = model.NewBoolVar(f'is_matching_any_pattern_{team_name}')
            model.Add(is_matching_any_pattern == 0)

        # Friday penalty for all sessions scheduled on Friday
        for idx, day_var in enumerate(day_vars):
            is_friday = model.NewBoolVar(f'is_friday_{team_name}_{idx}')
            model.Add(day_var == day_name_to_index['Fri']).OnlyEnforceIf(is_friday)
            model.Add(day_var != day_name_to_index['Fri']).OnlyEnforceIf(is_friday.Not())

            friday_penalty = model.NewIntVar(0, FRIDAY_PENALTY, f'friday_penalty_{team_name}_{idx}')
            model.Add(friday_penalty == FRIDAY_PENALTY * is_friday)
            penalties.append(friday_penalty)

    # Minimize total penalties
    total_penalty = sum(penalties)
    model.Minimize(total_penalty)