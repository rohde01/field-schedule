# Filename: main.py

from ortools.sat.python import cp_model
from test_data import get_teams, get_fields, get_5_star_constraints, get_3_star_constraints_girls
from utils import build_time_slots, get_subfields, get_size_to_combos, print_solution, get_subfield_availability, get_subfield_areas
from model import create_variables, add_constraints, solve_model
from collections import defaultdict

def main():
    """
    Main function to solve the soccer scheduling problem.
    """
    
    # Fetch constraints for boys and girls
    boys_constraints_list = get_5_star_constraints()
    girls_constraints_list = get_3_star_constraints_girls()
    constraints_list = []
    if boys_constraints_list != "NA":
        constraints_list.extend(boys_constraints_list)
    if girls_constraints_list != "NA":
        constraints_list.extend(girls_constraints_list)

    teams = get_teams()
    fields = get_fields()

    year_constraints = defaultdict(list)
    for constraint in constraints_list:
        year_constraints[constraint['year']].append(constraint)

    time_slots, all_days = build_time_slots(fields)
    all_subfields = get_subfields(fields)
    subfield_availability = get_subfield_availability(fields, time_slots, all_subfields)
    size_to_combos = get_size_to_combos(fields)
    subfield_areas = get_subfield_areas(fields)

    model = cp_model.CpModel()

    y_vars, session_combo_vars, x_vars = create_variables(
        model, teams, year_constraints, time_slots, size_to_combos
    )

    add_constraints(
        model, teams, year_constraints, time_slots, size_to_combos,
        y_vars, session_combo_vars, x_vars, subfield_areas, subfield_availability
    )

    solver, status = solve_model(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print_solution(solver, teams, time_slots, x_vars, all_subfields)
    else:
        print('No feasible solution found.')

if __name__ == "__main__":
    main()
