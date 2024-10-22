# filename: constraints.py

def add_team_session_constraints(model, teams, constraints, time_slots, size_to_combos,
                                 y_vars, session_combo_vars):
    """
    Adds constraints related to the number of sessions each team must have
    and limits sessions per day.
    """
    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraints = constraints[year]

        # Dictionary to track total sessions per day for the team
        daily_sessions = {day: [] for day in time_slots}

        for idx, team_constraint in enumerate(team_constraints):
            required_size = team_constraint['required_size']
            subfield_type = team_constraint['subfield_type']
            sessions = team_constraint['sessions']

            key = (required_size, subfield_type)
            possible_combos = size_to_combos.get(key, [])

            total_sessions = []
            for day in time_slots:
                # Add all session_combo_vars for this team and day
                for s in y_vars[team_name][idx][day]:
                    for combo in possible_combos:
                        total_sessions.append(session_combo_vars[team_name][idx][day][s][combo])
                        daily_sessions[day].append(session_combo_vars[team_name][idx][day][s][combo])

            # Constraint: Each team must have exactly 'sessions' sessions in total per constraint
            model.Add(sum(total_sessions) == sessions)

        # Constraint: At most one session per day across all constraints for the team
        for day in time_slots:
            model.Add(sum(daily_sessions[day]) <= 1)


def add_variable_linking_constraints(model, teams, constraints, time_slots, size_to_combos,
                                     y_vars, session_combo_vars, x_vars):
    """
    Adds constraints to link y_vars, session_combo_vars, and x_vars.
    """
    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraints = constraints[year]

        for idx, team_constraint in enumerate(team_constraints):
            required_size = team_constraint['required_size']
            subfield_type = team_constraint['subfield_type']
            length = team_constraint['length']

            key = (required_size, subfield_type)
            possible_combos = size_to_combos.get(key, [])

            for day in time_slots:
                # Link y_vars and session_combo_vars
                for s in y_vars[team_name][idx][day]:
                    session_vars = [session_combo_vars[team_name][idx][day][s][combo] for combo in possible_combos]
                    model.Add(y_vars[team_name][idx][day][s] == sum(session_vars))

                # Link session_combo_vars and x_vars
                num_slots_day = len(time_slots[day])
                for t in range(num_slots_day):
                    relevant_starts = [s for s in y_vars[team_name][idx][day] if s <= t < s + length]
                    for combo in possible_combos:
                        vars_in_sum = [session_combo_vars[team_name][idx][day][s][combo] for s in relevant_starts]
                        if vars_in_sum:
                            model.Add(x_vars[team_name][idx][day][t][combo] == sum(vars_in_sum))
                        else:
                            model.Add(x_vars[team_name][idx][day][t][combo] == 0)


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
                    team_constraints = constraints[year]
                    for idx, team_constraint in enumerate(team_constraints):
                        required_size = team_constraint['required_size']
                        subfield_type = team_constraint['subfield_type']

                        key = (required_size, subfield_type)
                        possible_combos = size_to_combos.get(key, [])

                        for combo in possible_combos:
                            if sf in combo:
                                if combo in x_vars[team_name][idx][day][t]:
                                    overlapping_vars.append(x_vars[team_name][idx][day][t][combo])
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
                # Collect all x_vars[team_name][idx][day][t][combo] for all idx and combo
                vars_at_t = []
                for idx in x_vars[team_name]:
                    vars_at_t.extend(x_vars[team_name][idx][day][t].values())
                # Constraint: A team cannot have more than one session at the same time
                model.Add(sum(vars_at_t) <= 1)

def add_field_availability_constraints(model, x_vars, time_slots, subfield_availability):
    """
    Adds constraints to ensure that fields are only used when they are available.
    """
    for team_name in x_vars:
        for idx in x_vars[team_name]:
            for day in time_slots:
                num_slots_day = len(time_slots[day])
                for t in range(num_slots_day):
                    for combo in x_vars[team_name][idx][day][t]:
                        # Check if all subfields in combo are available at time t on day
                        available = all(subfield_availability[sf][day][t] for sf in combo)
                        if not available:
                            # Set variable to 0 if any subfield in combo is unavailable
                            model.Add(x_vars[team_name][idx][day][t][combo] == 0)

