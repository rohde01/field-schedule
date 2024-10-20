from ortools.sat.python import cp_model
from constraints import (
    add_team_session_constraints,
    add_variable_linking_constraints,
    add_no_double_booking_constraints,
    add_no_overlapping_sessions_constraints
)


def create_variables(model, teams, constraints, time_slots, size_to_combos):
    """
    Creates decision variables for the model.
    """
    y_vars = {}  # y_vars[team][day][start_time_slot]
    session_combo_vars = {}  # session_combo_vars[team][day][start][combo]
    x_vars = {}  # x_vars[team][day][time_slot][combo]

    for team in teams:
        team_name = team['name']
        year = team['year']
        constraint = constraints[year]
        required_size = constraint['required_size']
        length = constraint['length']

        y_vars[team_name] = {}
        session_combo_vars[team_name] = {}
        x_vars[team_name] = {}

        for day in time_slots:
            num_slots_day = len(time_slots[day])
            possible_starts = list(range(num_slots_day - length + 1))

            y_vars[team_name][day] = {}
            session_combo_vars[team_name][day] = {}
            x_vars[team_name][day] = {}

            for s in possible_starts:
                y_var = model.NewBoolVar(f'y_{team_name}_{day}_{s}')
                y_vars[team_name][day][s] = y_var
                session_combo_vars[team_name][day][s] = {}
                for combo in size_to_combos[required_size]:
                    combo_name = '_'.join(combo)
                    var = model.NewBoolVar(f'session_{team_name}_{day}_{s}_{combo_name}')
                    session_combo_vars[team_name][day][s][combo] = var

            for t in range(num_slots_day):
                x_vars[team_name][day][t] = {}
                for combo in size_to_combos[required_size]:
                    combo_name = '_'.join(combo)
                    var = model.NewBoolVar(f'x_{team_name}_{day}_{t}_{combo_name}')
                    x_vars[team_name][day][t][combo] = var

    return y_vars, session_combo_vars, x_vars


def add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    y_vars, session_combo_vars, x_vars, all_subfields):
    """
    Adds all constraints to the model by delegating to specialized functions.
    """
    add_team_session_constraints(model, teams, constraints, time_slots, size_to_combos, y_vars, session_combo_vars)
    add_variable_linking_constraints(model, teams, constraints, time_slots, size_to_combos, y_vars, session_combo_vars, x_vars)
    add_no_double_booking_constraints(model, teams, constraints, time_slots, size_to_combos, x_vars, all_subfields)
    add_no_overlapping_sessions_constraints(model, teams, time_slots, x_vars)


def solve_model(model):
    """
    Solves the CP-SAT model.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status
