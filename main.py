from ortools.sat.python import cp_model
from data import get_teams, get_fields, get_constraints
from utils import build_time_slots, get_subfields, get_size_to_combos, print_solution
from model import create_variables, add_constraints, solve_model
from collections import defaultdict

def solve_soccer_scheduling():
    """
    Main function to solve the soccer scheduling problem.
    """
    # Data loading
    teams = get_teams()
    fields = get_fields()
    constraints_list = get_constraints()

    # Map years to a list of constraints
    year_constraints = defaultdict(list)
    for constraint in constraints_list:
        year_constraints[constraint['year']].append(constraint)

    # Build time slots and get all days
    time_slots, all_days = build_time_slots(fields)

    # Get all subfields
    all_subfields = get_subfields(fields)

    # Get field combinations per required size
    size_to_combos = get_size_to_combos(fields)

    # Initialize the model
    model = cp_model.CpModel()

    # Create variables
    y_vars, session_combo_vars, x_vars = create_variables(
        model, teams, year_constraints, time_slots, size_to_combos
    )

    # Add constraints
    add_constraints(
        model, teams, year_constraints, time_slots, size_to_combos,
        y_vars, session_combo_vars, x_vars, all_subfields
    )

    # Solve the model
    solver, status = solve_model(model)

    # Print the solution
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print_solution(solver, teams, time_slots, x_vars, all_subfields)
    else:
        print('No feasible solution found.')


def main():
    solve_soccer_scheduling()


if __name__ == "__main__":
    main()
