"""
Filename: main.py
Main module to solve the soccer scheduling problem.

Fetches data, builds the model, adds constraints, solves the model, and outputs the solution.
"""

import cProfile
import pstats
import argparse
from typing import List, Dict, Any
from ortools.sat.python import cp_model
from collections import defaultdict
from db import get_teams, get_fields, get_constraints, save_schedule
from utils import (
    build_time_slots,
    get_subfields,
    get_size_to_combos,
    get_subfield_availability,
    get_subfield_areas,
    get_cost_to_combos,
    get_field_costs,
    get_field_to_smallest_subfields,
)
from model import create_variables
from output import print_solution, print_raw_solution
from constraints import (
    add_no_overlapping_sessions_constraints,
    add_no_double_booking_constraints,
    add_field_availability_constraints,
    add_team_day_constraints,
    add_allowed_assignments_constraints
)


from objectives import add_objective_function

def add_objectives(model: cp_model.CpModel, teams: List[Any], interval_vars: Dict[int, Any], time_slots: Dict[str, List[str]], day_name_to_index: Dict[str, int]) -> None:
    """
    Adds an objective function to the model to minimize penalties for undesirable scheduling patterns
    and reward desirable ones.
    """
    add_objective_function(model, teams, interval_vars, time_slots, day_name_to_index)


def add_constraints(model: cp_model.CpModel, teams: List[Any], constraints: Dict[int, List[Any]], time_slots: Dict[str, List[str]], size_to_combos: Dict[Any, Any],
                    interval_vars: Dict[int, Any], assigned_fields: Dict[int, Any], subfield_areas: Dict[str, List[str]], subfield_availability: Dict[str, Dict[str, List[bool]]], global_time_slots: List[Any]) -> None:
    """
    Adds various constraints to the model.
    """
    add_no_overlapping_sessions_constraints(model, teams, interval_vars)
    add_no_double_booking_constraints(model, teams, interval_vars, assigned_fields, subfield_areas, global_time_slots)
    add_field_availability_constraints(model, interval_vars, assigned_fields, subfield_availability, global_time_slots)
    add_team_day_constraints(model, interval_vars)
    add_allowed_assignments_constraints(model, interval_vars)

def solve_model(model: cp_model.CpModel) -> Any:
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
    parser = argparse.ArgumentParser(description='Solve the soccer scheduling problem.')
    parser.add_argument('--raw', action='store_true', help='Print raw output instead of formatted output')
    parser.add_argument('--both', action='store_true', help='Print both tabular and raw output')
    parser.add_argument('--save', action='store_true', help='Save the generated schedule to the database')
    args = parser.parse_args()

    profiler = cProfile.Profile()
    profiler.enable()

    constraints_list = get_constraints()
    constraints: Dict[int, List[Any]] = {}
    for constraint in constraints_list:
        constraints.setdefault(constraint.team_id, []).append(constraint)

    teams = get_teams()
    fields = get_fields()
    field_name_to_id: Dict[str, int] = {}
    for field in fields:
        field_name_to_id[field.name] = field.field_id
        for half_subfield in field.half_subfields:
            field_name_to_id[half_subfield.name] = half_subfield.field_id
        for quarter_subfield in field.quarter_subfields:
            field_name_to_id[quarter_subfield.name] = quarter_subfield.field_id

    time_slots, all_days = build_time_slots(fields)
    all_subfields = get_subfields(fields)
    subfield_availability = get_subfield_availability(fields, time_slots, all_subfields)
    size_to_combos = get_size_to_combos(fields)
    subfield_areas = get_subfield_areas(fields)
    field_costs = get_field_costs()
    cost_to_combos = get_cost_to_combos(fields, field_costs)
    field_to_smallest_subfields, smallest_subfields_list = get_field_to_smallest_subfields(fields)

    parent_field_names = set()
    for field in fields:
        parent_field_names.add(field.name)
    parent_field_name_to_id = {name: idx for idx, name in enumerate(parent_field_names)}
    parent_field_id_to_name = {idx: name for name, idx in parent_field_name_to_id.items()}

    model = cp_model.CpModel()

    interval_vars, assigned_fields, global_time_slots, day_name_to_index = create_variables(
        model, teams, constraints, time_slots, size_to_combos, cost_to_combos, parent_field_name_to_id, fields
    )

    add_constraints(model, teams, constraints, time_slots, size_to_combos,
                    interval_vars, assigned_fields, subfield_areas, subfield_availability, global_time_slots)

    add_objectives(model, teams, interval_vars, time_slots, day_name_to_index)

    solver, status = solve_model(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        if args.raw:
            print_raw_solution(solver, teams, interval_vars, field_name_to_id)
        elif args.both:
            print_solution(solver, teams, time_slots, interval_vars, field_to_smallest_subfields, smallest_subfields_list)
            print_raw_solution(solver, teams, interval_vars, field_name_to_id)
        else:
            print_solution(solver, teams, time_slots, interval_vars, field_to_smallest_subfields, smallest_subfields_list)

        if args.save:
            save_schedule(solver, teams, interval_vars, field_name_to_id, club_id=1, constraints_list=constraints_list)
    else:
        print('No feasible solution found.')

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)

if __name__ == "__main__":
    main()
