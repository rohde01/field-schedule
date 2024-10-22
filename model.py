# filename: model.py

from ortools.sat.python import cp_model
from constraints import (
    add_team_session_constraints,
    add_variable_linking_constraints,
    add_no_double_booking_constraints,
    add_no_overlapping_sessions_constraints,
    add_field_availability_constraints
)

def create_variables(model, teams, constraints, time_slots, size_to_combos):
    """
    Creates decision variables for the model.
    """
    y_vars = {}  # y_vars[team][constraint_index][day][start_time_slot]
    session_combo_vars = {}  # session_combo_vars[team][constraint_index][day][start][combo]
    x_vars = {}  # x_vars[team][constraint_index][day][time_slot][combo]

    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraints = constraints[year]

        y_vars[team_name] = {}
        session_combo_vars[team_name] = {}
        x_vars[team_name] = {}

        for idx, constraint in enumerate(team_constraints):
            required_size = constraint['required_size']
            subfield_type = constraint['subfield_type']
            length = constraint['length']

            key = (required_size, subfield_type)
            possible_combos = size_to_combos.get(key, [])

            y_vars[team_name][idx] = {}
            session_combo_vars[team_name][idx] = {}
            x_vars[team_name][idx] = {}

            for day in time_slots:
                num_slots_day = len(time_slots[day])
                possible_starts = list(range(num_slots_day - length + 1))

                y_vars[team_name][idx][day] = {}
                session_combo_vars[team_name][idx][day] = {}
                x_vars[team_name][idx][day] = {}

                for s in possible_starts:
                    y_var = model.NewBoolVar(f'y_{team_name}_{idx}_{day}_{s}')
                    y_vars[team_name][idx][day][s] = y_var
                    session_combo_vars[team_name][idx][day][s] = {}
                    for combo in possible_combos:
                        combo_name = '_'.join(combo)
                        var = model.NewBoolVar(f'session_{team_name}_{idx}_{day}_{s}_{combo_name}')
                        session_combo_vars[team_name][idx][day][s][combo] = var

                for t in range(num_slots_day):
                    x_vars[team_name][idx][day][t] = {}
                    for combo in possible_combos:
                        combo_name = '_'.join(combo)
                        var = model.NewBoolVar(f'x_{team_name}_{idx}_{day}_{t}_{combo_name}')
                        x_vars[team_name][idx][day][t][combo] = var

    return y_vars, session_combo_vars, x_vars



def add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    y_vars, session_combo_vars, x_vars, all_subfields, subfield_availability):
    """
    Adds all constraints to the model by delegating to specialized functions.
    """
    add_team_session_constraints(model, teams, constraints, time_slots, size_to_combos, y_vars, session_combo_vars)
    add_variable_linking_constraints(model, teams, constraints, time_slots, size_to_combos, y_vars, session_combo_vars, x_vars)
    add_no_double_booking_constraints(model, teams, constraints, time_slots, size_to_combos, x_vars, all_subfields)
    add_no_overlapping_sessions_constraints(model, teams, time_slots, x_vars)
    add_field_availability_constraints(model, x_vars, time_slots, subfield_availability)  # Call the new function


def solve_model(model):
    """
    Solves the CP-SAT model.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status
