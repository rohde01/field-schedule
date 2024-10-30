# Filename: model.py

from ortools.sat.python import cp_model
from constraints import (
    add_no_overlapping_sessions_constraints,
    add_no_double_booking_constraints,
    add_field_availability_constraints
)

def create_variables(model, teams, constraints, time_slots, size_to_combos):
    """
    Creates interval variables for the model.
    """
    interval_vars = {}  # interval_vars[team][constraint_index][session_index]
    assigned_fields = {}  # assigned_fields[team][constraint_index][session_index]

    # Map time slots to global indices
    global_time_slots = []
    idx = 0
    idx_to_time = {}
    idx_to_day = []
    day_to_idx = {}
    for day in time_slots:
        day_to_idx[day] = idx  # Map day to index
        for t, slot_time in enumerate(time_slots[day]):
            idx_to_time[idx] = (day, t)
            global_time_slots.append((day, t))
            idx_to_day.append(list(time_slots.keys()).index(day))
            idx += 1
    num_global_slots = idx

    # For each team and each required session
    for team in teams:
        team_name = team['name']
        year = team['year']
        team_constraints = constraints[year]

        interval_vars[team_name] = {}
        assigned_fields[team_name] = {}

        for idx_constraint, constraint in enumerate(team_constraints):
            sessions = constraint['sessions']
            length = constraint['length']
            required_size = constraint['required_size']
            subfield_type = constraint['subfield_type']

            key = (required_size, subfield_type)
            possible_combos = size_to_combos.get(key, [])
            combo_indices = {combo: idx for idx, combo in enumerate(possible_combos)}

            interval_vars[team_name][idx_constraint] = []
            assigned_fields[team_name][idx_constraint] = []

            for session_idx in range(sessions):
                # Create variables:
                # Start variable, integer variable over possible start times
                # Duration is length
                # Interval variable
                # Assigned field combo variable

                start_var = model.NewIntVar(0, num_global_slots - length, f'start_{team_name}_{idx_constraint}_{session_idx}')
                end_var = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}')
                interval_var = model.NewIntervalVar(start_var, length, end_var, f'interval_{team_name}_{idx_constraint}_{session_idx}')

                if len(possible_combos) > 1:
                    assigned_combo = model.NewIntVar(0, len(possible_combos) - 1, f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}')
                else:
                    assigned_combo = model.NewConstant(0)

                # Create day variable
                day_var = model.NewIntVar(0, len(time_slots) - 1, f'day_{team_name}_{idx_constraint}_{session_idx}')
                # Link start_var to day_var using AddElement
                model.AddElement(start_var, idx_to_day, day_var)

                interval_vars[team_name][idx_constraint].append({
                    'start': start_var,
                    'end': end_var,
                    'interval': interval_var,
                    'length': length,
                    'constraint': constraint,
                    'assigned_combo': assigned_combo,
                    'possible_combos': possible_combos,
                    'combo_indices': combo_indices,
                    'day_var': day_var
                })

                assigned_fields[team_name][idx_constraint].append(assigned_combo)

    # After all variables are created, add the AllDifferent constraints for each team
    for team_name in interval_vars:
        team_day_vars = []
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
            for session in sessions:
                team_day_vars.append(session['day_var'])
        model.AddAllDifferent(team_day_vars)

    return interval_vars, assigned_fields, global_time_slots

def add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    interval_vars, assigned_fields, subfield_areas, subfield_availability, global_time_slots):
    add_no_overlapping_sessions_constraints(model, teams, interval_vars)
    add_no_double_booking_constraints(model, teams, interval_vars, assigned_fields, subfield_areas, global_time_slots)
    add_field_availability_constraints(model, interval_vars, assigned_fields, subfield_availability, global_time_slots)

def solve_model(model):
    """
    Solves the CP-SAT model.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status
