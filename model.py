"""
Filename: model.py
Model creation and solving functions for the scheduling problem.

Contains functions to create variables, add constraints, and solve the CP-SAT model.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
from constraints import (
    add_no_overlapping_sessions_constraints,
    add_no_double_booking_constraints,
    add_field_availability_constraints,
    add_team_day_constraints,
    add_allowed_assignments_constraints
)
from objectives import add_objective_function
from objectives import add_objective_function

def create_variables(model, teams, constraints, time_slots, size_to_combos):
    """
    Creates interval variables for the model.
    """
    # Build time slot mappings
    mappings = _build_time_slot_mappings(time_slots)
    global_time_slots = mappings['global_time_slots']
    day_name_to_index = mappings['day_name_to_index']

    interval_vars = {}
    assigned_fields = {}

    for team in teams:
        team_name = team['name']
        team_interval_vars, team_assigned_fields = _create_team_variables(
            model, team, constraints, time_slots, size_to_combos, mappings
        )
        interval_vars[team_name] = team_interval_vars
        assigned_fields[team_name] = team_assigned_fields

    return interval_vars, assigned_fields, global_time_slots, day_name_to_index

def _build_time_slot_mappings(time_slots):
    """Builds mappings from time slots to global indices and other related mappings."""
    global_time_slots = []
    idx = 0
    idx_to_time = {}
    idx_to_day = []
    day_to_idx = {}
    day_to_global_indices = defaultdict(list)
    day_names = list(time_slots.keys())
    day_name_to_index = {day_name: index for index, day_name in enumerate(day_names)}

    for day in time_slots:
        for t, slot_time in enumerate(time_slots[day]):
            idx_to_time[idx] = (day, t)
            global_time_slots.append((day, t))
            idx_to_day.append(day_name_to_index[day])
            day_to_global_indices[day].append(idx)
            idx += 1

    num_global_slots = idx

    return {
        'global_time_slots': global_time_slots,
        'idx_to_time': idx_to_time,
        'idx_to_day': idx_to_day,
        'day_to_global_indices': day_to_global_indices,
        'day_names': day_names,
        'day_name_to_index': day_name_to_index,
        'num_global_slots': num_global_slots
    }

def _create_team_variables(model, team, constraints, time_slots, size_to_combos, mappings):
    """Creates variables for a single team."""
    team_name = team['name']
    year = team['year']
    team_constraints = constraints[year]

    interval_vars = {}
    assigned_fields = {}

    for idx_constraint, constraint in enumerate(team_constraints):
        # Create variables for this constraint
        constraint_interval_vars, constraint_assigned_fields = _create_constraint_variables(
            model, team_name, idx_constraint, constraint, time_slots, size_to_combos, mappings
        )
        interval_vars[idx_constraint] = constraint_interval_vars
        assigned_fields[idx_constraint] = constraint_assigned_fields

    return interval_vars, assigned_fields

def _create_constraint_variables(model, team_name, idx_constraint, constraint, time_slots, size_to_combos, mappings):
    """Creates variables for a single constraint of a team."""
    sessions = constraint['sessions']
    length = constraint['length']
    required_size = constraint['required_size']
    subfield_type = constraint['subfield_type']

    key = (required_size, subfield_type)
    possible_combos = size_to_combos.get(key, [])
    combo_indices = {combo: idx for idx, combo in enumerate(possible_combos)}

    interval_vars = []
    assigned_fields = []

    for session_idx in range(sessions):
        # Create variables for this session
        session_vars = _create_session_variables(
            model, team_name, idx_constraint, session_idx, constraint, possible_combos, combo_indices, time_slots, mappings
        )
        interval_vars.append(session_vars)
        assigned_fields.append(session_vars['assigned_combo'])

    return interval_vars, assigned_fields

def _create_session_variables(model, team_name, idx_constraint, session_idx, constraint, possible_combos, combo_indices, time_slots, mappings):
    """Creates variables for a single session."""
    day_to_global_indices = mappings['day_to_global_indices']
    day_name_to_index = mappings['day_name_to_index']
    num_global_slots = mappings['num_global_slots']

    length = constraint['length']

    allowed_assignments = []
    allowed_start_times = set()

    for day_name in time_slots:
        day_idx = day_name_to_index[day_name]
        day_global_indices = day_to_global_indices[day_name]
        num_slots_day = len(day_global_indices)

        for s_local in range(num_slots_day - length + 1):
            s_global = day_global_indices[s_local]
            allowed_assignments.append([day_idx, s_global])
            allowed_start_times.add(s_global)

    allowed_start_times = sorted(allowed_start_times)
    start_var = model.NewIntVarFromDomain(
        cp_model.Domain.FromValues(allowed_start_times),
        f'start_{team_name}_{idx_constraint}_{session_idx}'
    )

    end_var = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}')
    interval_var = model.NewIntervalVar(
        start_var, length, end_var,
        f'interval_{team_name}_{idx_constraint}_{session_idx}'
    )

    if len(possible_combos) > 1:
        assigned_combo = model.NewIntVar(0, len(possible_combos) - 1,
                                         f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}')
    else:
        assigned_combo = model.NewConstant(0)

    day_var = model.NewIntVar(0, len(time_slots) - 1, f'day_{team_name}_{idx_constraint}_{session_idx}')

    # Note: The allowed assignments constraint is added in constraints.py
    session_vars = {
        'start': start_var,
        'end': end_var,
        'interval': interval_var,
        'length': length,
        'constraint': constraint,
        'assigned_combo': assigned_combo,
        'possible_combos': possible_combos,
        'combo_indices': combo_indices,
        'day_var': day_var,
        'allowed_assignments': allowed_assignments  # Pass this for constraint addition
    }

    return session_vars

def add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    interval_vars, assigned_fields, subfield_areas, subfield_availability, global_time_slots):
    """
    Adds various constraints to the model.
    """
    add_no_overlapping_sessions_constraints(model, teams, interval_vars)
    add_no_double_booking_constraints(model, teams, interval_vars, assigned_fields, subfield_areas, global_time_slots)
    add_field_availability_constraints(model, interval_vars, assigned_fields, subfield_availability, global_time_slots)
    add_team_day_constraints(model, interval_vars)
    add_allowed_assignments_constraints(model, interval_vars)

def add_objectives(model, teams, interval_vars, time_slots, day_name_to_index):
    """
    Adds an objective function to the model to minimize penalties for undesirable scheduling patterns
    and reward desirable ones.
    """
    add_objective_function(model, teams, interval_vars, time_slots, day_name_to_index)

def solve_model(model):
    """
    Solves the CP-SAT model.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status
