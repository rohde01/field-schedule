from ortools.sat.python import cp_model
from datetime import datetime, timedelta
from club_data import get_fields, get_teams
from dbu_requirements import get_5_star_constraints, get_3_star_constraints_girls
from excel_export import export_schedule_to_excel

# Constants
SIZE_TO_SUBFIELDS = {'full': 4, 'half': 2, 'quarter': 1, 'any': 1}
SESSION_LENGTH_MINUTES = 15

def generate_time_slots(fields):
    """Generates all available time slots based on fields' availability."""
    time_slots_set = set()
    for field in fields:
        for day, times in field['availability'].items():
            start_time = datetime.strptime(times['start'], '%H:%M')
            end_time = datetime.strptime(times['end'], '%H:%M')
            current_time = start_time
            while current_time + timedelta(minutes=SESSION_LENGTH_MINUTES) <= end_time:
                time_slot = f"{day}_{current_time.strftime('%H:%M')}"
                time_slots_set.add(time_slot)
                current_time += timedelta(minutes=SESSION_LENGTH_MINUTES)
    sorted_time_slots = sorted(time_slots_set)
    time_slot_indices = {ts: idx for idx, ts in enumerate(sorted_time_slots)}
    return sorted_time_slots, time_slot_indices

def get_year_constraints():
    """Fetches and organizes constraints by team year."""
    year_constraints = {}
    # Fetch constraints for boys
    boys_constraints_list = get_5_star_constraints()
    if boys_constraints_list:
        for constraint in boys_constraints_list:
            year = constraint['year']
            year_constraints.setdefault(year, []).append(constraint)
    # Fetch constraints for girls (currently not used)
    girls_constraints_list = get_3_star_constraints_girls()
    if girls_constraints_list:
        for constraint in girls_constraints_list:
            year = constraint['year']
            year_constraints.setdefault(year, []).append(constraint)
    return year_constraints

def filter_teams_by_constraints(teams, year_constraints):
    """Filters teams based on the available constraints."""
    valid_team_years = set(year_constraints.keys())
    return [team for team in teams if team['year'] in valid_team_years]

def extract_subfields(fields):
    """Extracts subfields and creates necessary mappings."""
    subfields = []
    subfield_to_field = {}
    field_subfields = {}
    for field in fields:
        field_subfields[field['name']] = field['subfields']
        for sf in field['subfields']:
            subfields.append(sf)
            subfield_to_field[sf] = field['name']
    subfield_indices = {sf: idx for idx, sf in enumerate(subfields)}
    return subfields, subfield_indices, subfield_to_field, field_subfields

def build_team_constraints(filtered_teams, year_constraints):
    """Builds team-specific constraints based on the year constraints."""
    team_constraints = []
    team_constraint_to_team = []
    team_constraints_indices_per_team = [[] for _ in filtered_teams]
    for t_idx, team in enumerate(filtered_teams):
        team_year = team['year']
        constraints = year_constraints[team_year]
        for constraint in constraints:
            tc_index = len(team_constraints)
            team_constraints.append({
                'team_index': t_idx,
                'required_size': constraint['required_size'],
                'sessions_required': constraint['sessions'],
                'length': constraint['length']
            })
            team_constraint_to_team.append(t_idx)
            team_constraints_indices_per_team[t_idx].append(tc_index)
    return team_constraints, team_constraint_to_team, team_constraints_indices_per_team

def create_cp_model(filtered_teams, team_constraints, fields, time_slots, time_slot_indices, field_subfields):
    """Creates the constraint programming model and variables."""
    model = cp_model.CpModel()
    team_sessions = {}
    for tc, constraint in enumerate(team_constraints):
        team_sessions[tc] = []
        sessions_required = constraint['sessions_required']
        session_length = constraint['length']
        for s in range(sessions_required):
            session = {'intervals': {}}
            for f_idx, field in enumerate(fields):
                # Get available time slots indices for the field
                field_available_ts_indices = []
                for ts in time_slots:
                    day, time_str = ts.split('_')
                    if day in field['availability']:
                        field_start = datetime.strptime(field['availability'][day]['start'], '%H:%M')
                        field_end = datetime.strptime(field['availability'][day]['end'], '%H:%M')
                        ts_time = datetime.strptime(time_str, '%H:%M')
                        if field_start <= ts_time <= field_end - timedelta(minutes=SESSION_LENGTH_MINUTES * session_length):
                            field_available_ts_indices.append(time_slot_indices[ts])
                if not field_available_ts_indices:
                    continue  # Field not available for this session length
                start_domain = field_available_ts_indices
                start_var = model.NewIntVarFromDomain(cp_model.Domain.FromValues(start_domain), f'start_tc{tc}_s{s}_f{f_idx}')
                presence_var = model.NewBoolVar(f'y_tc{tc}_s{s}_f{f_idx}')
                interval_var = model.NewOptionalIntervalVar(
                    start_var, session_length, start_var + session_length,
                    presence_var, f'session_tc{tc}_s{s}_f{f_idx}')
                session['intervals'][f_idx] = {
                    'interval': interval_var,
                    'start': start_var,
                    'presence_var': presence_var
                }
            team_sessions[tc].append(session)
    return model, team_sessions

def add_session_assignment_constraints(model, team_sessions):
    """Ensures each session is assigned to exactly one field."""
    for sessions in team_sessions.values():
        for session in sessions:
            presence_vars = [info['presence_var'] for info in session['intervals'].values()]
            model.AddExactlyOne(presence_vars)

def add_team_no_overlap_constraints(model, team_sessions):
    """Ensures sessions for the same team do not overlap."""
    for sessions in team_sessions.values():
        intervals = [info['interval'] for session in sessions for info in session['intervals'].values()]
        model.AddNoOverlap(intervals)

def add_subfield_constraints(model, team_sessions, team_constraints, fields, field_subfields, subfield_indices):
    """Enforces subfield resource constraints and assigns subfields to sessions."""
    x = {}
    subfield_intervals = {sf_idx: [] for sf_idx in subfield_indices.values()}
    for tc, sessions in team_sessions.items():
        required_subfields = SIZE_TO_SUBFIELDS[team_constraints[tc]['required_size']]
        session_length = team_constraints[tc]['length']
        for s_idx, session in enumerate(sessions):
            subfield_vars = []
            for f_idx, interval_info in session['intervals'].items():
                field = fields[f_idx]
                for sf in field_subfields[field['name']]:
                    sf_idx = subfield_indices[sf]
                    presence_var = model.NewBoolVar(f'x_tc{tc}_s{s_idx}_sf{sf_idx}_f{f_idx}')
                    x[(tc, s_idx, sf_idx)] = presence_var
                    # Link presence_var with session interval presence
                    model.AddImplication(presence_var, interval_info['presence_var'])
                    model.Add(presence_var <= interval_info['presence_var'])
                    # Create optional interval for subfield usage
                    optional_interval = model.NewOptionalIntervalVar(
                        interval_info['start'], session_length, interval_info['start'] + session_length,
                        presence_var, f'interval_sf{sf_idx}_tc{tc}_s{s_idx}_f{f_idx}')
                    subfield_intervals[sf_idx].append(optional_interval)
                    subfield_vars.append(presence_var)
            # Ensure required number of subfields are assigned per session
            model.Add(sum(subfield_vars) == required_subfields)
    # Enforce no overlap for subfields
    for intervals in subfield_intervals.values():
        model.AddNoOverlap(intervals)
    return x

def process_solution(solver, team_sessions, team_constraints, filtered_teams, fields, field_subfields, subfield_indices, time_slots, x):
    """Processes the solver's solution and constructs the schedule."""
    schedule = {ts: {sf: None for sf in subfield_indices.keys()} for ts in time_slots}
    for tc, sessions in team_sessions.items():
        t_idx = team_constraints[tc]['team_index']
        team_name = filtered_teams[t_idx]['name']
        for s_idx, session in enumerate(sessions):
            for f_idx, interval_info in session['intervals'].items():
                if solver.Value(interval_info['presence_var']):
                    start = solver.Value(interval_info['start'])
                    duration = team_constraints[tc]['length']
                    for offset in range(duration):
                        ts_idx = start + offset
                        if ts_idx >= len(time_slots):
                            continue  # Skip invalid timeslot indices
                        ts = time_slots[ts_idx]
                        for sf in field_subfields[fields[f_idx]['name']]:
                            sf_idx = subfield_indices[sf]
                            if (tc, s_idx, sf_idx) in x and solver.Value(x[(tc, s_idx, sf_idx)]):
                                if schedule[ts][sf] is None:
                                    schedule[ts][sf] = team_name
                                else:
                                    # Conflict detected, should not happen
                                    print(f"Conflict at timeslot {ts}, subfield {sf}")
    return schedule

def print_schedule(schedule, time_slots, subfields):
    """Prints the schedule in a tabular format."""
    header = ['Time'] + subfields
    print('Schedule:')
    print('\t'.join(header))
    for ts in time_slots:
        row = [ts.replace('_', ' ')] + [schedule[ts][sf] if schedule[ts][sf] else '-' for sf in subfields]
        print('\t'.join(row))

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
