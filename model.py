"""
Filename: model.py
Model creation and solving functions for the scheduling problem.

Contains functions to create variables, add constraints, and solve the CP-SAT model.
"""

from ortools.sat.python import cp_model
from collections import defaultdict
from utils import (
    _handle_start_time_constraint,
    get_parent_field,
    get_parent_field_ids,
    _get_allowed_assignments,
    _get_possible_combos
)


def create_variables(model, teams, constraints, time_slots, size_to_combos, cost_to_combos, parent_field_name_to_id):
    """
    Creates interval variables for the model.
    """
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
            cost_to_combos, mappings, parent_field_name_to_id
        )
        interval_vars[idx_constraint] = constraint_interval_vars
        assigned_fields[idx_constraint] = constraint_assigned_fields

    return interval_vars, assigned_fields


def _create_constraint_variables(model, team_name, idx_constraint, constraint, time_slots,
                                 size_to_combos, cost_to_combos, mappings, parent_field_name_to_id):
    """Creates variables for a single constraint of a team."""
    sessions = constraint['sessions']

    interval_vars = []
    assigned_fields = []

    possible_combos_part1, possible_combos_part2 = _get_possible_combos(constraint, size_to_combos, cost_to_combos)

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
    num_global_slots = mappings['num_global_slots']
    allowed_assignments, allowed_start_times = _get_allowed_assignments(constraint, time_slots, mappings)

    if 'partial_ses_time' in constraint:
        session_vars = _create_partial_session_variables(
            model, team_name, idx_constraint, session_idx, constraint,
            possible_combos_part1, combo_indices_part1,
            possible_combos_part2, combo_indices_part2,
            allowed_start_times, num_global_slots, time_slots,
            mappings, parent_field_name_to_id,
            allowed_assignments
        )
    else:
        session_vars = _create_regular_session_variables(
            model, team_name, idx_constraint, session_idx, constraint,
            possible_combos_part1, combo_indices_part1,
            allowed_start_times, num_global_slots, time_slots,
            allowed_assignments
        )

    return session_vars


def _create_partial_session_variables(model, team_name, idx_constraint, session_idx, constraint,
                                      possible_combos_part1, combo_indices_part1,
                                      possible_combos_part2, combo_indices_part2,
                                      allowed_start_times, num_global_slots, time_slots,
                                      mappings, parent_field_name_to_id,
                                      allowed_assignments):
    """Creates variables for a session with partial_ses_time."""
    partial_time = constraint['partial_ses_time']
    length1 = partial_time
    length2 = constraint['length'] - partial_time

    start_var1 = model.NewIntVarFromDomain(
        cp_model.Domain.FromValues(allowed_start_times),
        f'start_{team_name}_{idx_constraint}_{session_idx}_part1'
    )
    end_var1 = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}_part1')
    interval_var1 = model.NewIntervalVar(
        start_var1, length1, end_var1,
        f'interval_{team_name}_{idx_constraint}_{session_idx}_part1'
    )

    start_var2 = model.NewIntVar(0, num_global_slots, f'start_{team_name}_{idx_constraint}_{session_idx}_part2')
    end_var2 = model.NewIntVar(0, num_global_slots, f'end_{team_name}_{idx_constraint}_{session_idx}_part2')
    interval_var2 = model.NewIntervalVar(
        start_var2, length2, end_var2,
        f'interval_{team_name}_{idx_constraint}_{session_idx}_part2'
    )

    model.Add(start_var2 == end_var1)

    start_var = start_var1
    end_var = end_var2

    assigned_combo1 = model.NewIntVar(0, len(possible_combos_part1) - 1,
                                      f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}_part1')
    assigned_combo2 = model.NewIntVar(0, len(possible_combos_part2) - 1,
                                      f'assigned_combo_{team_name}_{idx_constraint}_{session_idx}_part2')
    day_var = model.NewIntVar(0, len(time_slots) - 1, f'day_{team_name}_{idx_constraint}_{session_idx}')
    assigned_parent_field = model.NewIntVar(0, len(parent_field_name_to_id) - 1,
                                            f'assigned_parent_field_{team_name}_{idx_constraint}_{session_idx}')
    parent_field_ids_part1 = get_parent_field_ids(possible_combos_part1, parent_field_name_to_id)
    parent_field_ids_part2 = get_parent_field_ids(possible_combos_part2, parent_field_name_to_id)

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

    return session_vars


def _create_regular_session_variables(model, team_name, idx_constraint, session_idx, constraint,
                                      possible_combos_part1, combo_indices_part1,
                                      allowed_start_times, num_global_slots, time_slots,
                                      allowed_assignments):
    """Creates variables for a regular session without partial_ses_time."""
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
    if 'start_time' in constraint:
        model.Add(start_var == allowed_start_times[0])

    return session_vars
