# Filename: main.py
# Discription: Main script to run the scheduling algorithm

from club_data import get_fields, get_teams
from config import SIZE_TO_SUBFIELDS, SESSION_LENGTH_MINUTES
from utils import (
    generate_time_slots,
    extract_subfields,
    filter_teams_by_constraints,
    build_team_constraints,
    get_year_constraints,
)
from constraints import (
    add_session_assignment_constraints,
    add_team_no_overlap_constraints,
    add_subfield_constraints,
)
from model import create_cp_model, process_solution
from output import print_schedule, export_schedule_to_excel
from ortools.sat.python import cp_model

def main():
    fields = get_fields()
    teams = get_teams()
    # Generate dynamic time slots based on fields' availability
    time_slots, time_slot_indices = generate_time_slots(fields)
    # Fetch constraints and build mapping
    year_constraints = get_year_constraints()
    # Filter teams based on defined constraints
    filtered_teams = filter_teams_by_constraints(teams, year_constraints)
    # Extract subfields and create mappings
    subfields, subfield_indices, _, field_subfields = extract_subfields(fields)
    # Build team constraints
    team_constraints, _, _ = build_team_constraints(filtered_teams, year_constraints)
    # Create the model and variables
    model, team_sessions = create_cp_model(filtered_teams, team_constraints, fields, time_slots, time_slot_indices, field_subfields)
    # Add constraints to the model
    add_session_assignment_constraints(model, team_sessions)
    add_team_no_overlap_constraints(model, team_sessions)
    x = add_subfield_constraints(model, team_sessions, team_constraints, fields, field_subfields, subfield_indices)
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    # Process and display the solution
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        schedule = process_solution(solver, team_sessions, team_constraints, filtered_teams, fields, field_subfields, subfield_indices, time_slots, x)
        print_schedule(schedule, time_slots, subfields)
        # Export schedule to Excel
        export_schedule_to_excel(schedule, fields, time_slots)
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
