def add_team_session_constraints(model, teams, constraints, time_slots, size_to_combos,
                                 y_vars, session_combo_vars):
    """
    Adds constraints related to the number of sessions each team must have
    and limits sessions per day.
    """
    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraint = constraints[year]
        required_size = team_constraint['required_size']
        sessions = team_constraint['sessions']

        total_sessions = []
        for day in time_slots:
            # Add all session_combo_vars for this team and day
            for s in y_vars[team_name][day]:
                for combo in size_to_combos[required_size]:
                    total_sessions.append(session_combo_vars[team_name][day][s][combo])

            # Constraint: At most one session per day for each team
            model.Add(sum(y_vars[team_name][day].values()) <= 1)

        # Constraint: Each team must have exactly 'sessions' sessions in total
        model.Add(sum(total_sessions) == sessions)


def add_variable_linking_constraints(model, teams, constraints, time_slots, size_to_combos,
                                     y_vars, session_combo_vars, x_vars):
    """
    Adds constraints to link y_vars, session_combo_vars, and x_vars.
    """
    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraint = constraints[year]
        required_size = team_constraint['required_size']
        length = team_constraint['length']

        for day in time_slots:
            # Link y_vars and session_combo_vars
            for s in y_vars[team_name][day]:
                session_vars = session_combo_vars[team_name][day][s].values()
                model.Add(y_vars[team_name][day][s] == sum(session_vars))

            # Link session_combo_vars and x_vars
            num_slots_day = len(time_slots[day])
            for t in range(num_slots_day):
                relevant_starts = [s for s in y_vars[team_name][day] if s <= t < s + length]
                for combo in size_to_combos[required_size]:
                    vars_in_sum = [session_combo_vars[team_name][day][s][combo] for s in relevant_starts]
                    if vars_in_sum:
                        model.Add(x_vars[team_name][day][t][combo] == sum(vars_in_sum))
                    else:
                        model.Add(x_vars[team_name][day][t][combo] == 0)


def add_no_double_booking_constraints(model, teams, constraints, time_slots, size_to_combos,
                                      x_vars, all_subfields):
    """
    Adds constraints to prevent double-booking of subfields.
    """
    for day in time_slots:
        num_slots_day = len(time_slots[day])
        for t in range(num_slots_day):
            for sf in all_subfields:
                overlapping_vars = []
                for team in teams:
                    team_name = team['name']
                    year = team['year']
                    required_size = constraints[year]['required_size']
                    for combo in size_to_combos[required_size]:
                        if sf in combo:
                            overlapping_vars.append(x_vars[team_name][day][t][combo])
                # Constraint: No double-booking of subfields
                model.Add(sum(overlapping_vars) <= 1)


def add_no_overlapping_sessions_constraints(model, teams, time_slots, x_vars):
    """
    Adds constraints to prevent overlapping sessions for the same team.
    """
    for team in teams:
        team_name = team['name']
        for day in time_slots:
            num_slots_day = len(time_slots[day])
            for t in range(num_slots_day):
                # Constraint: A team cannot have more than one session at the same time
                model.Add(sum(x_vars[team_name][day][t].values()) <= 1)
