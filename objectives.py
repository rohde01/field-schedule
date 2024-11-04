from ortools.sat.python import cp_model


def add_objective_function(model, teams, interval_vars, time_slots, day_name_to_index):
    """
    Adds an objective function to the model to minimize penalties for undesirable scheduling patterns
    and reward desirable ones.
    """
    CONSECUTIVE_DAY_PENALTY = 100
    PENALTY_PER_DAY_DEVIATION = 200
    DAY_WEIGHT_PENALTY = 10
    less_favored_day = 'Friday'

    num_days = len(day_name_to_index)
    day_weights = [1.0] * num_days
    if less_favored_day in day_name_to_index:
        day_weights[day_name_to_index[less_favored_day]] = 1.5

    penalties = []

    preferred_patterns = {
        2: [[2]],
        3: [[2, 2]],
        4: [[1, 2, 1]]
    }

    for team in teams:
        team_name = team['name']
        team_sessions = [session for sessions in interval_vars[team_name].values() for session in sessions]
        day_vars = [session['day_var'] for session in team_sessions]
        num_sessions = len(day_vars)

        # Penalty for consecutive training days
        for i in range(num_sessions - 1):
            day_diff = model.NewIntVar(0, num_days, f'day_diff_{team_name}_{i}')
            model.Add(day_diff == day_vars[i+1] - day_vars[i])

            is_consecutive = model.NewBoolVar(f'is_consecutive_{team_name}_{i}')
            model.Add(day_diff == 1).OnlyEnforceIf(is_consecutive)
            model.Add(day_diff != 1).OnlyEnforceIf(is_consecutive.Not())

            penalty = model.NewIntVar(0, CONSECUTIVE_DAY_PENALTY, f'penalty_consecutive_{team_name}_{i}')
            model.Add(penalty == CONSECUTIVE_DAY_PENALTY * is_consecutive)
            penalties.append(penalty)

        # Penalty for deviation from preferred patterns
        if num_sessions in preferred_patterns:
            pattern_penalties = []
            for pattern_num, pattern in enumerate(preferred_patterns[num_sessions]):
                diffs = [
                    model.NewIntVar(-num_days, num_days, f'pattern_{pattern_num}_day_diff_{team_name}_{i}')
                    for i in range(len(pattern))
                ]
                for i, expected_diff in enumerate(pattern):
                    model.Add(diffs[i] == day_vars[i+1] - day_vars[i])
                    deviation = model.NewIntVar(0, num_days, f'pattern_{pattern_num}_deviation_{team_name}_{i}')
                    model.AddAbsEquality(deviation, diffs[i] - expected_diff)
                    diffs[i] = deviation

                total_deviation = model.NewIntVar(0, num_days * len(pattern), f'pattern_{pattern_num}_total_deviation_{team_name}')
                model.Add(total_deviation == sum(diffs))

                pattern_penalty = model.NewIntVar(0, num_days * PENALTY_PER_DAY_DEVIATION, f'pattern_{pattern_num}_penalty_{team_name}')
                model.Add(pattern_penalty == total_deviation * PENALTY_PER_DAY_DEVIATION)
                pattern_penalties.append(pattern_penalty)

            min_pattern_penalty = model.NewIntVar(0, num_days * PENALTY_PER_DAY_DEVIATION, f'min_pattern_penalty_{team_name}')
            model.AddMinEquality(min_pattern_penalty, pattern_penalties)
            penalties.append(min_pattern_penalty)

        # Penalty for less favored days
        for i, day_var in enumerate(day_vars):
            day_penalty = model.NewIntVar(0, DAY_WEIGHT_PENALTY * num_days, f'day_penalty_{team_name}_{i}')
            weighted_penalty = sum(
                int(day_weights[day_index] * DAY_WEIGHT_PENALTY) *
                model.NewBoolVar(f'is_day_{team_name}_{i}_{day_index}')
                for day_index in day_name_to_index.values()
            )
            model.Add(day_penalty == weighted_penalty)
            penalties.append(day_penalty)

    total_penalty = model.NewIntVar(0, 1000000, 'total_penalty')
    model.Add(total_penalty == sum(penalties))
    model.Minimize(total_penalty)