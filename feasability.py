from ortools.sat.python import cp_model
from club_data import get_fields, get_teams, get_time_slots
from dbu_requirements import get_5_star_constraints, get_4_star_constraints
from excel_export import export_schedule_to_excel

def main():
    
    fields = get_fields()

    teams = get_teams()

    time_slots = get_time_slots()

    year_constraints = get_5_star_constraints() # get_4_star_constraints

    # Extract subfields and create a mapping from subfield to field
    subfields = []
    subfield_to_field = {}
    field_subfields = {}
    for field in fields:
        field_name = field['name']
        field_subfields[field_name] = field['subfields']
        for sf in field['subfields']:
            subfields.append(sf)
            subfield_to_field[sf] = field_name

    # Build indices for teams, timeslots, subfields, and fields
    team_indices = {team['name']: idx for idx, team in enumerate(teams)}
    timeslot_indices = {ts: idx for idx, ts in enumerate(time_slots)}
    subfield_indices = {sf: idx for idx, sf in enumerate(subfields)}
    field_indices = {field['name']: idx for idx, field in enumerate(fields)}

    num_teams = len(teams)
    num_timeslots = len(time_slots)
    num_subfields = len(subfields)
    num_fields = len(fields)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    x = {}
    y = {}
    ts_assigned = {}
    for t in range(num_teams):
        for ts in range(num_timeslots):
            ts_assigned[(t, ts)] = model.NewBoolVar(f'ts_assigned_{t}_{ts}')
            for sf in range(num_subfields):
                x[(t, ts, sf)] = model.NewBoolVar(f'x_{t}_{ts}_{sf}')
            for f in range(num_fields):
                y[(t, ts, f)] = model.NewBoolVar(f'y_{t}_{ts}_{f}')

    # Constraint 1: Each subfield at each timeslot is assigned to at most one team
    for ts in range(num_timeslots):
        for sf in range(num_subfields):
            model.Add(sum(x[(t, ts, sf)] for t in range(num_teams)) <= 1)

    # Read field size requirements and session counts from year_constraints
    team_field_requirements = []
    team_sessions_required = []
    size_to_subfields = {'full': 4, 'half': 2, 'quarter': 1}
    for t, team in enumerate(teams):
        team_year = team['year']
        if team_year in year_constraints:
            required_size = year_constraints[team_year].get('required_size', 'any')
            sessions_required = year_constraints[team_year].get('sessions', 1)
        else:
            required_size = 'any'
            sessions_required = 3  # Default value
        team_field_requirements.append(required_size)
        team_sessions_required.append(sessions_required)

    # Constraint: Each team is assigned to the required number of sessions
    for t in range(num_teams):
        sessions_required = team_sessions_required[t]
        required_size = team_field_requirements[t]
        required_subfields = size_to_subfields.get(required_size, 1)
        model.Add(sum(ts_assigned[(t, ts)] for ts in range(num_timeslots)) == sessions_required)

        for ts in range(num_timeslots):
            # Ensure that if a team is assigned to a timeslot, they are assigned to exactly one field
            model.Add(ts_assigned[(t, ts)] == sum(y[(t, ts, f)] for f in range(num_fields)))

            # Link ts_assigned and x variables
            model.Add(sum(x[(t, ts, sf)] for sf in range(num_subfields)) == required_subfields * ts_assigned[(t, ts)])

            for f in range(num_fields):
                field_name = fields[f]['name']
                field_sf_indices = [subfield_indices[sf] for sf in field_subfields[field_name]]

                # Link y and x variables
                for sf_idx in field_sf_indices:
                    model.Add(x[(t, ts, sf_idx)] <= y[(t, ts, f)])
                # Ensure that sum of x over the field equals required_subfields times y
                model.Add(sum(x[(t, ts, sf_idx)] for sf_idx in field_sf_indices) == required_subfields * y[(t, ts, f)])

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Initialize the schedule
    schedule = {}
    for ts in range(num_timeslots):
        schedule[time_slots[ts]] = {}
        for sf in range(num_subfields):
            schedule[time_slots[ts]][subfields[sf]] = None

    # Populate the schedule with the solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for t in range(num_teams):
            team_name = teams[t]['name']
            for ts in range(num_timeslots):
                for sf in range(num_subfields):
                    if solver.Value(x[(t, ts, sf)]):
                        schedule[time_slots[ts]][subfields[sf]] = team_name

        # Prepare the headers
        header = ['Time'] + subfields
        print('Schedule:')
        print('\t'.join(header))

        # Print the schedule
        for ts in time_slots:
            row = [ts.replace('_', ' ')]
            for sf in subfields:
                assignment = schedule[ts][sf]
                row.append(assignment if assignment else '-')
            print('\t'.join(row))

        # Export schedule to Excel
        export_schedule_to_excel(schedule, fields, time_slots)
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()