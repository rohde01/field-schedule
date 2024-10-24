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

        daily_sessions = {day: [] for day in time_slots}

        for idx, team_constraint in enumerate(team_constraints):
            required_size = team_constraint['required_size']
            subfield_type = team_constraint['subfield_type']
            sessions = team_constraint['sessions']

            key = (required_size, subfield_type)
            possible_combos = size_to_combos.get(key, [])

            total_sessions = []
            for day in time_slots:
                for s in y_vars[team_name][idx][day]:
                    for combo in possible_combos:
                        total_sessions.append(session_combo_vars[team_name][idx][day][s][combo])
                        daily_sessions[day].append(session_combo_vars[team_name][idx][day][s][combo])

            model.Add(sum(total_sessions) == sessions)

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
                for s in y_vars[team_name][idx][day]:
                    session_vars = [session_combo_vars[team_name][idx][day][s][combo] for combo in possible_combos]
                    model.Add(y_vars[team_name][idx][day][s] == sum(session_vars))

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
                                      x_vars, subfield_areas):
    """
    Adds constraints to prevent double-booking of subfields.
    """
    for day in time_slots:
        num_slots_day = len(time_slots[day])
        for t in range(num_slots_day):
            area_vars = {}
            for team in teams:
                team_name = team['name']
                year = team['year']
                team_constraints = constraints[year]
                for idx, team_constraint in enumerate(team_constraints):
                    for combo, var in x_vars[team_name][idx][day][t].items():
                        areas = set()
                        for sf in combo:
                            areas.update(subfield_areas[sf])
                        for area in areas:
                            area_vars.setdefault(area, []).append(var)
            for area, vars_in_area in area_vars.items():
                model.Add(sum(vars_in_area) <= 1)

def add_no_overlapping_sessions_constraints(model, teams, time_slots, x_vars):
    """
    Adds constraints to prevent overlapping sessions for the same team.
    """
    for team in teams:
        team_name = team['name']
        for day in time_slots:
            num_slots_day = len(time_slots[day])
            for t in range(num_slots_day):
                vars_at_t = []
                for idx in x_vars[team_name]:
                    vars_at_t.extend(x_vars[team_name][idx][day][t].values())
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
                        available = all(subfield_availability[sf][day][t] for sf in combo)
                        if not available:
                            model.Add(x_vars[team_name][idx][day][t][combo] == 0)
