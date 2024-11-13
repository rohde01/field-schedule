"""
Filename: main.py
Main module to solve the soccer scheduling problem.

Fetches data, builds the model, adds constraints, solves the model, and outputs the solution.
"""

import cProfile
import pstats
from ortools.sat.python import cp_model
from collections import defaultdict
from test_data import get_teams, get_fields, get_5_star_constraints, get_3_star_constraints_girls
from utils import build_time_slots, get_subfields, get_size_to_combos, get_subfield_availability, get_subfield_areas, get_cost_to_combos, get_field_costs
from model import create_variables, solve_model
from output import get_field_to_smallest_subfields, print_solution
from model import add_constraints
from collections import defaultdict
from model import add_objectives


def main():
    """
    Main function to solve the soccer scheduling problem.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    boys_constraints_list = get_5_star_constraints()
    girls_constraints_list = get_3_star_constraints_girls()
    constraints_list = []
    if boys_constraints_list != "NA":
        constraints_list.extend(boys_constraints_list)
    if girls_constraints_list != "NA":
        constraints_list.extend(girls_constraints_list)

    teams = get_teams()
    fields = get_fields()
    field_to_smallest_subfields, smallest_subfields_list = get_field_to_smallest_subfields(fields)

    year_constraints = defaultdict(list)
    for constraint in constraints_list:
        year_constraints[constraint['year']].append(constraint)

    time_slots, all_days = build_time_slots(fields)
    all_subfields = get_subfields(fields)
    subfield_availability = get_subfield_availability(fields, time_slots, all_subfields)
    size_to_combos = get_size_to_combos(fields)
    subfield_areas = get_subfield_areas(fields)
    field_costs = get_field_costs()
    cost_to_combos = get_cost_to_combos(fields, field_costs)

    model = cp_model.CpModel()
    
    interval_vars, assigned_fields, global_time_slots, day_name_to_index = create_variables(
        model, teams, year_constraints, time_slots, size_to_combos, cost_to_combos 
    )

    add_constraints(model, teams, constraints_list, time_slots, size_to_combos,
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
