# Filename: config.py
# Description: Configuration file for the scheduling algorithm.

# Constants
SIZE_TO_SUBFIELDS = {'full': 4, 'half': 2, 'quarter': 1, 'any': 1}
SESSION_LENGTH_MINUTES = 15
# Filename: club_data.py
# Discription: Data source for the scheduling algorithm

def get_fields():
    return [
        {
            'name': 'Græs 1',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G1-1', 'G1-2', 'G1-3', 'G1-4'],
            'availability': {
                'Mon': {'start': '16:00', 'end': '21:00'},
                'Tue': {'start': '16:00', 'end': '21:00'},
                'Wed': {'start': '16:00', 'end': '21:00'},
                'Thu': {'start': '16:00', 'end': '21:00'},
                'Fri': {'start': '16:00', 'end': '21:00'},
            }
        },

        {
            'name': 'Græs 2',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G2-1', 'G2-2', 'G2-3', 'G2-4'],
            'availability': {
                'Mon': {'start': '16:00', 'end': '21:00'},
                'Tue': {'start': '16:00', 'end': '21:00'},
                'Wed': {'start': '16:00', 'end': '21:00'},
                'Thu': {'start': '16:00', 'end': '21:00'},
                'Fri': {'start': '16:00', 'end': '21:00'},
            }
        },

        {
            'name': 'Græs 3',
            'surface': 'grass',
            'size': 'full',
            'subfields': ['G3-1', 'G3-2', 'G3-3', 'G3-4'],
            'availability': {
                'Mon': {'start': '16:00', 'end': '21:00'},
                'Tue': {'start': '16:00', 'end': '21:00'},
                'Wed': {'start': '16:00', 'end': '21:00'},
                'Thu': {'start': '16:00', 'end': '21:00'},
                'Fri': {'start': '16:00', 'end': '21:00'},
            }
        },
        
    ]


def get_teams():
    return [
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
# Filename: constraints.py
# Description: Constraint generation functions for the scheduling algorithm.

from config import SIZE_TO_SUBFIELDS, SESSION_LENGTH_MINUTES

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

def add_team_single_session_per_day_constraints(model, team_sessions, time_slots):
    day_names = sorted(set(ts.split('_')[0] for ts in time_slots))
    day_to_index = {day: idx for idx, day in enumerate(day_names)}
    time_slot_idx_to_day_index = [day_to_index[ts.split('_')[0]] for ts in time_slots]
    for tc, sessions in team_sessions.items():
        day_vars = []
        for s_idx, session in enumerate(sessions):
            day_var = model.NewIntVar(0, len(day_names)-1, f'day_var_tc{tc}_s{s_idx}')
            day_vars.append(day_var)
            for interval_info in session['intervals'].values():
                start_var = interval_info['start']
                presence_var = interval_info['presence_var']
                local_day_var = model.NewIntVar(0, len(day_names)-1, f'local_day_var_tc{tc}_s{s_idx}')
                model.AddElement(start_var, time_slot_idx_to_day_index, local_day_var)
                model.Add(day_var == local_day_var).OnlyEnforceIf(presence_var)
        model.AddAllDifferent(day_vars)
# Filename: dbu_requirements.py
# Description: This file contains the requirements for each year group and the number of sessions required for each year group.

def get_5_star_constraints():
    return [
        #U19
        {'year': 'U19', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U19', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U17
        {'year': 'U17', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U17', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U15
        {'year': 'U15', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U15', 'required_size': 'half', 'sessions': 1, 'length': 4},
        {'year': 'U15', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U14
        {'year': 'U14', 'required_size': 'half', 'sessions': 1, 'length': 4},
        {'year': 'U14', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U13
        {'year': 'U13', 'required_size': 'half', 'sessions': 1, 'length': 4},
        {'year': 'U13', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U12
        {'year': 'U12', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U11
        {'year': 'U11', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
        #U10
        {'year': 'U10', 'required_size': 'quarter', 'sessions': 1, 'length': 4},
    ]

def get_3_star_constraints_girls():
    return [
        #U19-girl
        {'year': 'U19-girl', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U19-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U16-girl
        {'year': 'U16-girl', 'required_size': 'full', 'sessions': 1, 'length': 4},
        {'year': 'U16-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U14-girl
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        {'year': 'U14-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        #U13-girl
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
        {'year': 'U13-girl', 'required_size': 'half', 'sessions': 1, 'length': 4},
    ]
# Filename: model.py
# Description: Constraint programming model creation and solution processing functions.

from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from config import SIZE_TO_SUBFIELDS, SESSION_LENGTH_MINUTES

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
# Filename: utils.py
# Description: Utility functions for the scheduling algorithm.

from datetime import datetime, timedelta
from config import SESSION_LENGTH_MINUTES
from dbu_requirements import get_5_star_constraints, get_3_star_constraints_girls

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


def filter_teams_by_constraints(teams, year_constraints):
    """Filters teams based on the available constraints."""
    valid_team_years = set(year_constraints.keys())
    return [team for team in teams if team['year'] in valid_team_years]


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
    add_team_single_session_per_day_constraints,
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
    add_team_single_session_per_day_constraints(model, team_sessions, time_slots)
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

