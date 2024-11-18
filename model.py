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
from utils import _handle_start_time_constraint, get_parent_field

def create_variables(model, teams, constraints, time_slots, size_to_combos, cost_to_combos, parent_field_name_to_id):
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
        team_id = team['team_id']
        team_constraints = constraints[team_id]
        team_interval_vars, team_assigned_fields = _create_team_variables(
            model, team, team_constraints, time_slots, size_to_combos, cost_to_combos, mappings, parent_field_name_to_id
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

def _create_team_variables(model, team, team_constraints, time_slots, size_to_combos, cost_to_combos, mappings, parent_field_name_to_id):
    """Creates variables for a single team."""
    team_name = team['name']

    interval_vars = {}
    assigned_fields = {}

    for idx_constraint, constraint in enumerate(team_constraints):
        constraint_interval_vars, constraint_assigned_fields = _create_constraint_variables(
            model, team_name, idx_constraint, constraint, time_slots, size_to_combos, 
            cost_to_combos, mappings, parent_field_name_to_id  # Add parent_field_name_to_id here
        )
        interval_vars[idx_constraint] = constraint_interval_vars
        assigned_fields[idx_constraint] = constraint_assigned_fields

    return interval_vars, assigned_fields

def _create_constraint_variables(model, team_name, idx_constraint, constraint, time_slots,
                                 size_to_combos, cost_to_combos, mappings, parent_field_name_to_id):
    """Creates variables for a single constraint of a team."""
    sessions = constraint['sessions']
    length = constraint['length']

    interval_vars = []
    assigned_fields = []

    # Determine possible field combinations based on constraint type
    if 'required_cost' in constraint:
        required_cost = constraint['required_cost']
        possible_combos_part1 = cost_to_combos.get(required_cost, [])
    else:
        key_part1 = (constraint['required_size'], constraint['subfield_type'])
        possible_combos_part1 = size_to_combos.get(key_part1, [])

    if 'partial_ses_time' in constraint:
        # Need to compute possible_combos for the second part
        if 'partial_ses_space' in constraint:
            if 'required_cost' in constraint:
                required_cost_part2 = constraint['partial_ses_space']
                possible_combos_part2 = cost_to_combos.get(required_cost_part2, [])
            else:
                key_part2 = (constraint['required_size'], constraint['partial_ses_space'])
                possible_combos_part2 = size_to_combos.get(key_part2, [])
        else:
            possible_combos_part2 = possible_combos_part1
    else:
        possible_combos_part2 = possible_combos_part1

    # For both parts, we need to compute combo_indices
    combo_indices_part1 = {combo: idx for idx, combo in enumerate(possible_combos_part1)}
    combo_indices_part2 = {combo: idx for idx, combo in enumerate(possible_combos_part2)}

    for session_idx in range(sessions):
        session_vars = _create_session_variables(
            model, team_name, idx_constraint, session_idx, constraint,
            possible_combos_part1, combo_indices_part1,
            possible_combos_part2, combo_indices_part2,
            time_slots, mappings, parent_field_name_to_id
        )
        interval_vars.append(session_vars)
        assigned_fields.append(session_vars['assigned_combos'])

    return interval_vars, assigned_fields

def _create_session_variables(model, team_name, idx_constraint, session_idx, constraint,
                              possible_combos_part1, combo_indices_part1,
                              possible_combos_part2, combo_indices_part2,
                              time_slots, mappings, parent_field_name_to_id):
    """Creates variables for a single session, including handling partial sessions."""
    day_to_global_indices = mappings['day_to_global_indices']
    day_name_to_index = mappings['day_name_to_index']
    num_global_slots = mappings['num_global_slots']

    # Get allowed assignments and start times
    if 'start_time' in constraint:
        allowed_assignments, allowed_start_times = _handle_start_time_constraint(constraint, time_slots, mappings)
    else:
        allowed_assignments = []
        allowed_start_times = set()
        for day_name in time_slots:
            day_idx = day_name_to_index[day_name]
            day_global_indices = day_to_global_indices[day_name]
            num_slots_day = len(day_global_indices)
            total_length = constraint['length']
            for s_local in range(num_slots_day - total_length + 1):
                s_global = day_global_indices[s_local]
                allowed_assignments.append([day_idx, s_global])
                allowed_start_times.add(s_global)

    # Create model variables
    allowed_start_times = sorted(allowed_start_times)

    if 'partial_ses_time' in constraint:
        partial_time = constraint['partial_ses_time']
        length1 = partial_time
        length2 = constraint['length'] - partial_time

        # First part
        start_var1 = model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(allowed_start_times),
            f'start_{team_name}_{idx_constraint}_{session_idx}_part1'
        )
        end_var1 = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}_part1')
        interval_var1 = model.NewIntervalVar(
            start_var1, length1, end_var1,
            f'interval_{team_name}_{idx_constraint}_{session_idx}_part1'
        )

        # Second part
        start_var2 = model.NewIntVar(0, num_global_slots, f'start_{team_name}_{idx_constraint}_{session_idx}_part2')
        end_var2 = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}_part2')
        interval_var2 = model.NewIntervalVar(
            start_var2, length2, end_var2,
            f'interval_{team_name}_{idx_constraint}_{session_idx}_part2'
        )

        model.Add(start_var2 == end_var1)

        start_var = start_var1
        end_var = end_var2

        # Assigned combos for each part
        assigned_combo1 = model.NewIntVar(0, len(possible_combos_part1) - 1,
                                          f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}_part1')
        assigned_combo2 = model.NewIntVar(0, len(possible_combos_part2) - 1,
                                          f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}_part2')

        day_var = model.NewIntVar(0, len(time_slots) - 1, f'day_{team_name}_{idx_constraint}_{session_idx}')

        assigned_parent_field = model.NewIntVar(0, len(parent_field_name_to_id) - 1,
                                                f'assigned_parent_field_{team_name}_{idx_constraint}_{session_idx}')

        # Map combo indices to parent field IDs for part1
        parent_field_ids_part1 = []
        for combo in possible_combos_part1:
            parent_field = get_parent_field(combo[0])
            parent_field_id = parent_field_name_to_id[parent_field]
            parent_field_ids_part1.append(parent_field_id)

        # Map combo indices to parent field IDs for part2
        parent_field_ids_part2 = []
        for combo in possible_combos_part2:
            parent_field = get_parent_field(combo[0])
            parent_field_id = parent_field_name_to_id[parent_field]
            parent_field_ids_part2.append(parent_field_id)

        model.AddElement(assigned_combo1, parent_field_ids_part1, assigned_parent_field)
        model.AddElement(assigned_combo2, parent_field_ids_part2, assigned_parent_field)

        session_vars = {
            'start': start_var,
            'end': end_var,
            'intervals': [interval_var1, interval_var2],
            'start_vars': [start_var1, start_var2],
            'end_vars': [end_var1, end_var2],
            'lengths': [length1, length2],
            'constraint': constraint,
            'assigned_combos': [assigned_combo1, assigned_combo2],
            'possible_combos': [possible_combos_part1, possible_combos_part2],
            'combo_indices': [combo_indices_part1, combo_indices_part2],
            'day_var': day_var,
            'allowed_assignments': allowed_assignments,
            'assigned_parent_field': assigned_parent_field
        }

        if 'start_time' in constraint:
            model.Add(start_var1 == allowed_start_times[0])

    else:
        # Regular session
        start_var = model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(allowed_start_times),
            f'start_{team_name}_{idx_constraint}_{session_idx}'
        )

        end_var = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}')
        interval_var = model.NewIntervalVar(
            start_var, constraint['length'], end_var,
            f'interval_{team_name}_{idx_constraint}_{session_idx}'
        )

        if len(possible_combos_part1) > 1:
            assigned_combo1 = model.NewIntVar(0, len(possible_combos_part1) - 1,
                                             f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}')
        else:
            assigned_combo1 = model.NewConstant(0)

        day_var = model.NewIntVar(0, len(time_slots) - 1, f'day_{team_name}_{idx_constraint}_{session_idx}')

        session_vars = {
            'start': start_var,
            'end': end_var,
            'intervals': [interval_var],
            'start_vars': [start_var],
            'end_vars': [end_var],
            'lengths': [constraint['length']],
            'constraint': constraint,
            'assigned_combos': [assigned_combo1],
            'possible_combos': [possible_combos_part1],
            'combo_indices': [combo_indices_part1],
            'day_var': day_var,
            'allowed_assignments': allowed_assignments
        }

        # If start_time is specified, add constraint to fix start_var
        if 'start_time' in constraint:
            model.Add(start_var == allowed_start_times[0])

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
