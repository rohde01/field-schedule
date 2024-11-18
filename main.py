"""
Filename: main.py
Main module to solve the soccer scheduling problem.

Fetches data, builds the model, adds constraints, solves the model, and outputs the solution.
"""

import cProfile
import pstats
from ortools.sat.python import cp_model
from collections import defaultdict
from test_data import get_teams, get_fields, get_constraints
from utils import build_time_slots, get_subfields, get_size_to_combos, get_subfield_availability, get_subfield_areas, get_cost_to_combos, get_field_costs
from model import create_variables
from output import get_field_to_smallest_subfields, print_solution
from collections import defaultdict
from constraints import (
    add_no_overlapping_sessions_constraints,
    add_no_double_booking_constraints,
    add_field_availability_constraints,
    add_team_day_constraints,
    add_allowed_assignments_constraints
)
from objectives import add_objective_function

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

def main():
    """
    Main function to solve the soccer scheduling problem.
    """
    profiler = cProfile.Profile()
    profiler.enable()

    constraints_list = get_constraints()
    constraints = {}
    for constraint in constraints_list:
        constraints.setdefault(constraint['team_id'], []).append(constraint)

    teams = get_teams()
    fields = get_fields()
    field_to_smallest_subfields, smallest_subfields_list = get_field_to_smallest_subfields(fields)

    time_slots, all_days = build_time_slots(fields)
    all_subfields = get_subfields(fields)
    subfield_availability = get_subfield_availability(fields, time_slots, all_subfields)
    size_to_combos = get_size_to_combos(fields)
    subfield_areas = get_subfield_areas(fields)
    field_costs = get_field_costs()
    cost_to_combos = get_cost_to_combos(fields, field_costs)

    parent_field_names = set()
    for field in fields:
        parent_field_names.add(field['name'])
    parent_field_name_to_id = {name: idx for idx, name in enumerate(parent_field_names)}
    parent_field_id_to_name = {idx: name for name, idx in parent_field_name_to_id.items()}

    model = cp_model.CpModel()
    
    interval_vars, assigned_fields, global_time_slots, day_name_to_index = create_variables(
        model, teams, constraints, time_slots, size_to_combos, cost_to_combos, parent_field_name_to_id
    )

    add_constraints(model, teams, constraints, time_slots, size_to_combos,
                interval_vars, assigned_fields, subfield_areas, subfield_availability, global_time_slots)
    
    add_objectives(model, teams, interval_vars, time_slots, day_name_to_index)

    solver, status = solve_model(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print_solution(solver, teams, time_slots, interval_vars, field_to_smallest_subfields, smallest_subfields_list, global_time_slots)
    else:
        print('No feasible solution found.')

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)

if __name__ == "__main__":
    main()
