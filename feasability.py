from ortools.sat.python import cp_model
from club_data import get_fields, get_teams, get_time_slots
from dbu_requirements import get_5_star_constraints, get_4_star_constraints
from excel_export import export_schedule_to_excel

def main():
    fields = get_fields()
    teams = get_teams()
    time_slots = get_time_slots()
    year_constraints = get_5_star_constraints()

    # Extract subfields and create a mapping from subfield to field
    subfields = [sf for field in fields for sf in field['subfields']]
    subfield_to_field = {sf: field['name'] for field in fields for sf in field['subfields']}
    field_subfields = {field['name']: field['subfields'] for field in fields}

    # Build indices for teams, timeslots, subfields, and fields
    subfield_indices = {sf: idx for idx, sf in enumerate(subfields)}
    num_teams = len(teams)
    num_timeslots = len(time_slots)
    num_subfields = len(subfields)
    num_fields = len(fields)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    x = {(t, ts, sf): model.NewBoolVar(f'x_{t}_{ts}_{sf}') for t in range(num_teams) for ts in range(num_timeslots) for sf in range(num_subfields)}
    y = {(t, ts, f): model.NewBoolVar(f'y_{t}_{ts}_{f}') for t in range(num_teams) for ts in range(num_timeslots) for f in range(num_fields)}
    ts_assigned = {(t, ts): model.NewBoolVar(f'ts_assigned_{t}_{ts}') for t in range(num_teams) for ts in range(num_timeslots)}

    # Constraint 1: Each subfield at each timeslot is assigned to at most one team
    for ts in range(num_timeslots):
        for sf in range(num_subfields):
            model.Add(sum(x[(t, ts, sf)] for t in range(num_teams)) <= 1)

    # Read field size requirements and session counts from year_constraints
    size_to_subfields = {'full': 4, 'half': 2, 'quarter': 1}
    team_field_requirements = []
    team_sessions_required = []
    for team in teams:
        team_year = team['year']
        required_size = year_constraints.get(team_year, {}).get('required_size', 'any')
        sessions_required = year_constraints.get(team_year, {}).get('sessions', 3)
        team_field_requirements.append(required_size)
        team_sessions_required.append(sessions_required)

    # Constraint: Each team is assigned to the required number of sessions
    for t in range(num_teams):
        required_subfields = size_to_subfields.get(team_field_requirements[t], 1)
        model.Add(sum(ts_assigned[(t, ts)] for ts in range(num_timeslots)) == team_sessions_required[t])

        for ts in range(num_timeslots):
            # Ensure that if a team is assigned to a timeslot, they are assigned to exactly one field
            model.Add(ts_assigned[(t, ts)] == sum(y[(t, ts, f)] for f in range(num_fields)))

            # Link ts_assigned and x variables
            model.Add(sum(x[(t, ts, sf)] for sf in range(num_subfields)) == required_subfields * ts_assigned[(t, ts)])

            for f in range(num_fields):
                field_sf_indices = [subfield_indices[sf] for sf in field_subfields[fields[f]['name']]]

                # Link y and x variables
                for sf_idx in field_sf_indices:
                    model.Add(x[(t, ts, sf_idx)] <= y[(t, ts, f)])
                model.Add(sum(x[(t, ts, sf_idx)] for sf_idx in field_sf_indices) == required_subfields * y[(t, ts, f)])

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Initialize and populate the schedule with the solution
    schedule = {ts: {sf: None for sf in subfields} for ts in time_slots}
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for t in range(num_teams):
            team_name = teams[t]['name']
            for ts in range(num_timeslots):
                for sf in range(num_subfields):
                    if solver.Value(x[(t, ts, sf)]):
                        schedule[time_slots[ts]][subfields[sf]] = team_name

        # Print the schedule
        header = ['Time'] + subfields
        print('Schedule:')
        print('\t'.join(header))
        for ts in time_slots:
            row = [ts.replace('_', ' ')] + [schedule[ts][sf] if schedule[ts][sf] else '-' for sf in subfields]
            print('\t'.join(row))

        # Export schedule to Excel
        export_schedule_to_excel(schedule, fields, time_slots)
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
