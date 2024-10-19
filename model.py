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