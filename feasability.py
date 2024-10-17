from ortools.sat.python import cp_model
import xlsxwriter

def main():
    # Fields
    fields = [
        {
            'name': 'Græs 1',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G1-1', 'G1-2', 'G1-3', 'G1-4']
        },
        {
            'name': 'Græs 2',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G2-1', 'G2-2', 'G2-3', 'G2-4']
        },
        {
            'name': 'Græs 3',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G3-1', 'G3-2', 'G3-3', 'G3-4']
        },
    ]

    # Teams
    teams = [
        {'name': 'U19A', 'level': 'academy', 'gender': 'boys', 'year': 'U19'},
        {'name': 'U17A', 'level': 'academy', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U19-2', 'level': 'youth', 'gender': 'boys', 'year': 'U19'},
        {'name': 'U19A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U19-girl'},
        {'name': 'U15A', 'level': 'academy', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U14A', 'level': 'academy', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U13A', 'level': 'academy', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U14A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U14-girl'},
        {'name': 'U13A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U13-girl'},
        {'name': 'U16A-girl', 'level': 'academy', 'gender': 'girls', 'year': 'U16-girl'},
        {'name': 'U12A', 'level': 'academy', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U17-2', 'level': 'youth', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U11A', 'level': 'academy', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U10A', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U15-2', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U15-3', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U14-2', 'level': 'youth', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U14-3', 'level': 'youth', 'gender': 'boys', 'year': 'U14'},
        {'name': 'U13-2', 'level': 'youth', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U11-A', 'level': 'child', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U13-3', 'level': 'youth', 'gender': 'boys', 'year': 'U13'},
        {'name': 'U12-B', 'level': 'youth', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U11-B', 'level': 'youth', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U17-3', 'level': 'youth', 'gender': 'boys', 'year': 'U17'},
        {'name': 'U15-4', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
        {'name': 'U12-B+', 'level': 'youth', 'gender': 'boys', 'year': 'U12'},
        {'name': 'U11-B+', 'level': 'youth', 'gender': 'boys', 'year': 'U11'},
        {'name': 'U10-B+', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U16-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U16-girl'},
        {'name': 'U14-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U14-girl'},
        {'name': 'U13-2-girl', 'level': 'youth', 'gender': 'girls', 'year': 'U13-girl'},
        {'name': 'U10-B', 'level': 'child', 'gender': 'boys', 'year': 'U10'},
        {'name': 'U15-5', 'level': 'youth', 'gender': 'boys', 'year': 'U15'},
    ]
    # Time slots
    time_slots = [
        'Mon_16:00', 'Mon_17:30', 'Mon_19:00',
        'Tue_16:00', 'Tue_17:30', 'Tue_19:00',
        'Wed_16:00', 'Wed_17:30', 'Wed_19:00',
        'Thu_16:00', 'Thu_17:30', 'Thu_19:00',
        'Fri_16:00', 'Fri_17:30', 'Fri_19:00',
    ]

    # General constraints for teams based on their year
    year_constraints = {
        'U19': {'required_size': 'full', 'sessions': 2},
        'U17': {'required_size': 'full', 'sessions': 2},
        'U15': {'required_size': 'full', 'sessions': 1},
        'U14': {'required_size': 'half', 'sessions': 3},
        'U13': {'required_size': 'half', 'sessions': 3},
        'U10': {'required_size': 'quarter', 'sessions': 2},
        'U11': {'required_size': 'quarter', 'sessions': 2},
        'U12': {'required_size': 'quarter', 'sessions': 2},
        'U13-girl': {'required_size': 'half', 'sessions': 3},
        'U14-girl': {'required_size': 'half', 'sessions': 3},
        'U16-girl': {'required_size': 'full', 'sessions': 2},
        'U19-girl': {'required_size': 'full', 'sessions': 2},
    }

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
        workbook = xlsxwriter.Workbook('schedule.xlsx')
        worksheet = workbook.add_worksheet()

        # Define bold format for headers
        bold_format = workbook.add_format({'bold': True})

        # Write the headers to the Excel file with bold format
        current_col = 0
        worksheet.write(0, current_col, 'Time', bold_format)
        current_col += 1
        for field in fields:
            for subfield in field['subfields']:
                worksheet.write(0, current_col, subfield, bold_format)
                current_col += 1
            # Add a blank column for spacing after each group of subfields
            worksheet.set_column(current_col, current_col, None)
            current_col += 1

        # Write the schedule data to the Excel file with spacing between groups of subfields
        current_row = 1
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
            for ts in time_slots:
                if ts.startswith(day):
                    current_col = 0
                    worksheet.write(current_row, current_col, ts.replace('_', ' '), bold_format)
                    current_col += 1
                    for field in fields:
                        for subfield in field['subfields']:
                            assignment = schedule[ts][subfield]
                            worksheet.write(current_row, current_col, assignment if assignment else '-')
                            current_col += 1
                        # Add a blank column for spacing after each group of subfields
                        current_col += 1
                    current_row += 1
            # Add a blank row to separate each day's timeslots
            current_row += 1

        workbook.close()
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
