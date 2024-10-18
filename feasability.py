from ortools.sat.python import cp_model
from club_data import get_fields, get_teams, get_time_slots
from dbu_requirements import get_5_star_constraints, get_3_star_constraints_girls
from excel_export import export_schedule_to_excel

def main():
    fields = get_fields()
    teams = get_teams()
    time_slots = get_time_slots()

    # Fetch constraints for boys and girls
    boys_constraints_list = get_5_star_constraints()
    girls_constraints_list = 'NA' #get_3_star_constraints_girls()

    year_constraints_list = []
    if boys_constraints_list != "NA":
        year_constraints_list.extend(boys_constraints_list)
    if girls_constraints_list != "NA":
        year_constraints_list.extend(girls_constraints_list)

    # Build mapping from 'year' to list of constraints
    year_constraints = {}
    for constraint in year_constraints_list:
        year = constraint['year']
        if year not in year_constraints:
            year_constraints[year] = []
        year_constraints[year].append({'required_size': constraint['required_size'], 'sessions': constraint['sessions']})

    # Filter teams based on defined constraints
    valid_team_years = set(year_constraints.keys())
    filtered_teams = [team for team in teams if team['year'] in valid_team_years]

    # Extract subfields and create a mapping from subfield to field
    subfields = [sf for field in fields for sf in field['subfields']]
    subfield_to_field = {sf: field['name'] for field in fields for sf in field['subfields']}
    field_subfields = {field['name']: field['subfields'] for field in fields}

    # Build indices for teams, timeslots, subfields, and fields
    subfield_indices = {sf: idx for idx, sf in enumerate(subfields)}
    num_teams = len(filtered_teams)
    num_timeslots = len(time_slots)
    num_subfields = len(subfields)
    num_fields = len(fields)

    # Create the model
    model = cp_model.CpModel()

    # Build team constraints
    team_constraints = []
    team_constraint_to_team = []
    team_constraints_indices_per_team = [[] for _ in filtered_teams]  # list per team
    for t, team in enumerate(filtered_teams):
        team_year = team['year']
        constraints = year_constraints.get(team_year, [{'required_size': 'any', 'sessions': 3}])
        for c in constraints:
            tc_index = len(team_constraints)
            team_constraints.append({
                'team_index': t,
                'required_size': c['required_size'],
                'sessions_required': c['sessions']
            })
            team_constraint_to_team.append(t)
            team_constraints_indices_per_team[t].append(tc_index)

    num_team_constraints = len(team_constraints)

    # Variables
    x = {}
    y = {}
    ts_assigned = {}
    for tc in range(num_team_constraints):
        for ts in range(num_timeslots):
            ts_assigned[(tc, ts)] = model.NewBoolVar(f'ts_assigned_{tc}_{ts}')
            for f in range(num_fields):
                y[(tc, ts, f)] = model.NewBoolVar(f'y_{tc}_{ts}_{f}')
            for sf in range(num_subfields):
                x[(tc, ts, sf)] = model.NewBoolVar(f'x_{tc}_{ts}_{sf}')

    # Constraint 1: Each subfield at each timeslot is assigned to at most one team_constraint
    for ts in range(num_timeslots):
        for sf in range(num_subfields):
            model.Add(sum(x[(tc, ts, sf)] for tc in range(num_team_constraints)) <= 1)

    # Size mapping
    size_to_subfields = {'full': 4, 'half': 2, 'quarter': 1, 'any': 1}

    # Constraints for each team constraint
    for tc in range(num_team_constraints):
        required_subfields = size_to_subfields[team_constraints[tc]['required_size']]
        sessions_required = team_constraints[tc]['sessions_required']

        # Ensure that the total number of sessions is met
        model.Add(sum(ts_assigned[(tc, ts)] for ts in range(num_timeslots)) == sessions_required)

        for ts in range(num_timeslots):
            # Ensure that if a team constraint is assigned to a timeslot, they are assigned to exactly one field
            model.Add(ts_assigned[(tc, ts)] == sum(y[(tc, ts, f)] for f in range(num_fields)))

            # Link ts_assigned and x variables
            model.Add(sum(x[(tc, ts, sf)] for sf in range(num_subfields)) == required_subfields * ts_assigned[(tc, ts)])

            for f in range(num_fields):
                field_sf_indices = [subfield_indices[sf] for sf in field_subfields[fields[f]['name']]]

                # Link y and x variables
                model.Add(sum(x[(tc, ts, sf_idx)] for sf_idx in field_sf_indices) == required_subfields * y[(tc, ts, f)])

                for sf_idx in field_sf_indices:
                    model.Add(x[(tc, ts, sf_idx)] <= y[(tc, ts, f)])

    # Ensure a team is not assigned more than one of its constraints in the same timeslot
    for t in range(num_teams):
        for ts in range(num_timeslots):
            model.Add(sum(ts_assigned[(tc, ts)] for tc in team_constraints_indices_per_team[t]) <= 1)

    # Create the solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Initialize and populate the schedule with the solution
    schedule = {ts: {sf: None for sf in subfields} for ts in time_slots}
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for tc in range(num_team_constraints):
            t = team_constraints[tc]['team_index']
            team_name = filtered_teams[t]['name']
            for ts in range(num_timeslots):
                for sf in range(num_subfields):
                    if solver.Value(x[(tc, ts, sf)]):
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
