from ortools.sat.python import cp_model
from datetime import datetime, timedelta
from club_data import get_fields, get_teams
from dbu_requirements import get_5_star_constraints, get_3_star_constraints_girls
from excel_export import export_schedule_to_excel

def generate_time_slots(fields):
    time_slots_set = set()
    for field in fields:
        for day, times in field['availability'].items():
            start_time = datetime.strptime(times['start'], '%H:%M')
            end_time = datetime.strptime(times['end'], '%H:%M')
            current_time = start_time
            while current_time + timedelta(minutes=15) <= end_time:
                time_slot = f"{day}_{current_time.strftime('%H:%M')}"
                time_slots_set.add(time_slot)
                current_time += timedelta(minutes=15)
    sorted_time_slots = sorted(list(time_slots_set))
    time_slot_indices = {ts: idx for idx, ts in enumerate(sorted_time_slots)}
    return sorted_time_slots, time_slot_indices

def main():
    fields = get_fields()
    teams = get_teams()
    # Generate dynamic time slots based on fields' availability
    time_slots, time_slot_indices = generate_time_slots(fields)
    
    # Fetch constraints for boys and girls
    boys_constraints_list = get_5_star_constraints()
    girls_constraints_list = 'NA'  # get_3_star_constraints_girls()
    
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
        year_constraints[year].append({
            'required_size': constraint['required_size'],
            'sessions': constraint['sessions'],
            'length': constraint['length']
        })
    
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
        constraints = year_constraints.get(team_year, [{'required_size': 'any', 'sessions': 3, 'length': 4}])
        for c in constraints:
            tc_index = len(team_constraints)
            team_constraints.append({
                'team_index': t,
                'required_size': c['required_size'],
                'sessions_required': c['sessions'],
                'length': c['length']
            })
            team_constraint_to_team.append(t)
            team_constraints_indices_per_team[t].append(tc_index)
    
    num_team_constraints = len(team_constraints)
    
    # Size mapping
    size_to_subfields = {'full': 4, 'half': 2, 'quarter': 1, 'any': 1}
    
    # Variables for sessions
    team_sessions = {}
    for tc, constraint in enumerate(team_constraints):
        team_sessions[tc] = []
        sessions_required = constraint['sessions_required']
        session_length = constraint['length']
        required_subfields = size_to_subfields[constraint['required_size']]
        for s in range(sessions_required):
            session = {}
            session['intervals'] = {}
            # For each field, create an optional interval variable
            for f, field in enumerate(fields):
                # Get available time slots indices for the field
                field_available_ts_indices = []
                for ts in time_slots:
                    day, time_str = ts.split('_')
                    if day in field['availability']:
                        field_start = datetime.strptime(field['availability'][day]['start'], '%H:%M')
                        field_end = datetime.strptime(field['availability'][day]['end'], '%H:%M')
                        ts_time = datetime.strptime(time_str, '%H:%M')
                        if field_start <= ts_time <= field_end - timedelta(minutes=15 * session_length):
                            field_available_ts_indices.append(time_slot_indices[ts])
                if not field_available_ts_indices:
                    continue  # Field not available for this session length
                start_domain = field_available_ts_indices
                start_var = model.NewIntVarFromDomain(cp_model.Domain.FromValues(start_domain), f'start_tc{tc}_s{s}_f{f}')
                presence_var = model.NewBoolVar(f'y_tc{tc}_s{s}_f{f}')
                interval_var = model.NewOptionalIntervalVar(
                    start_var, session_length, start_var + session_length, 
                    presence_var, f'session_tc{tc}_s{s}_f{f}')
                session['intervals'][f] = {
                    'interval': interval_var, 
                    'start': start_var, 
                    'presence_var': presence_var
                }
            team_sessions[tc].append(session)
    
    # Ensure that each session is assigned to exactly one field
    for tc in team_sessions:
        for s, session in enumerate(team_sessions[tc]):
            y_vars = []
            for f in session['intervals']:
                y_var = session['intervals'][f]['presence_var']
                y_vars.append(y_var)
            model.AddExactlyOne(y_vars)
    
    # Ensure sessions do not overlap for the same team
    for tc in team_sessions:
        intervals = []
        for s, session in enumerate(team_sessions[tc]):
            for f in session['intervals']:
                intervals.append(session['intervals'][f]['interval'])
        model.AddNoOverlap(intervals)
    
    # Assignment variables x
    x = {}  # x[(tc, s, sf)] = 1 if session s of team tc uses subfield sf
    
    # Enforce subfield resource constraints
    for sf_idx, sf in enumerate(subfields):
        intervals = []
        for tc in team_sessions:
            for s, session in enumerate(team_sessions[tc]):
                for f, field in enumerate(fields):
                    if f in session['intervals']:
                        if sf in field_subfields[field['name']]:
                            presence_var = model.NewBoolVar(f'x_tc{tc}_s{s}_sf{sf_idx}_f{f}')
                            x[(tc, s, sf_idx)] = presence_var
                            interval = session['intervals'][f]['interval']
                            # Link presence_var with interval presence
                            model.AddImplication(presence_var, session['intervals'][f]['presence_var'])
                            # Ensure that if the interval is present, the subfield is used
                            model.Add(presence_var <= session['intervals'][f]['presence_var'])
                            optional_interval = model.NewOptionalIntervalVar(
                                interval.StartExpr(), interval.SizeExpr(), interval.EndExpr(), 
                                presence_var, f'interval_sf{sf_idx}_tc{tc}_s{s}_f{f}')
                            intervals.append(optional_interval)
        model.AddNoOverlap(intervals)
    
    # Ensure required number of subfields are assigned per session
    for tc in team_sessions:
        for s, session in enumerate(team_sessions[tc]):
            required_subfields = size_to_subfields[team_constraints[tc]['required_size']]
            subfield_vars = []
            for f in session['intervals']:
                for sf in field_subfields[fields[f]['name']]:
                    sf_idx = subfield_indices[sf]
                    if (tc, s, sf_idx) in x:
                        subfield_vars.append(x[(tc, s, sf_idx)])
            model.Add(sum(subfield_vars) == required_subfields)
    
    # Create the solver and solve
    solver = cp_model.CpSolver()
    # Uncomment the next line to see the solver's progress
    # solver.parameters.log_search_progress = True
    status = solver.Solve(model)
    
    # Initialize and populate the schedule with the solution
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        schedule = {ts: {sf: None for sf in subfields} for ts in time_slots}
        for tc in team_sessions:
            t = team_constraints[tc]['team_index']
            team_name = filtered_teams[t]['name']
            for s, session in enumerate(team_sessions[tc]):
                for f in session['intervals']:
                    interval = session['intervals'][f]['interval']
                    if solver.Value(session['intervals'][f]['presence_var']):
                        start = solver.Value(interval.StartExpr())
                        duration = team_constraints[tc]['length']
                        for offset in range(duration):
                            ts_idx = start + offset
                            if ts_idx >= len(time_slots):
                                continue  # Skip invalid timeslot indices
                            ts = time_slots[ts_idx]
                            for sf in field_subfields[fields[f]['name']]:
                                sf_idx = subfield_indices[sf]
                                if (tc, s, sf_idx) in x and solver.Value(x[(tc, s, sf_idx)]):
                                    if schedule[ts][sf] is None:
                                        schedule[ts][sf] = team_name
                                    else:
                                        # Conflict detected, should not happen
                                        print(f"Conflict at timeslot {ts}, subfield {sf}")
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
