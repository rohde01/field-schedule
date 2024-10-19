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