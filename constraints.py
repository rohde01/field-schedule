"""
Filename: constraints.py
Constraint functions for the scheduling model.

Provides functions to add various constraints to the CP-SAT model to prevent overlapping sessions,
double booking, enforce field availability, and ensure sessions are on different days.
"""

def add_no_overlapping_sessions_constraints(model, teams, interval_vars):
    """
    Adds constraints to prevent overlapping sessions for the same team.
    """
    for team in teams:
        team_name = team['name']
        team_intervals = []
        for idx in interval_vars[team_name]:
            for session in interval_vars[team_name][idx]:
                team_intervals.append(session['interval'])
        model.AddNoOverlap(team_intervals)

def add_no_double_booking_constraints(model, teams, interval_vars, assigned_fields, subfield_areas, global_time_slots):
    """
    Adds constraints to prevent double-booking of subfields.
    """
    subfield_intervals = {}

    for team in teams:
        team_name = team['name']
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
            for session_idx, session in enumerate(sessions):
                assigned_combo_var = session['assigned_combo']
                combo_indices = session['combo_indices']

                for combo, combo_index in combo_indices.items():
                    subfields = set()
                    for field in combo:
                        subfields.update(subfield_areas[field])

                    uses_combo = model.NewBoolVar(f'uses_{team_name}_{idx_constraint}_{session_idx}_{combo_index}')
                    model.Add(assigned_combo_var == combo_index).OnlyEnforceIf(uses_combo)
                    model.Add(assigned_combo_var != combo_index).OnlyEnforceIf(uses_combo.Not())

                    for sf in subfields:
                        if sf not in subfield_intervals:
                            subfield_intervals[sf] = []
                        sf_interval = model.NewOptionalIntervalVar(
                            session['start'], session['length'], session['end'], uses_combo,
                            f'sf_interval_{team_name}_{idx_constraint}_{session_idx}_{sf}'
                        )
                        subfield_intervals[sf].append(sf_interval)

    for sf in subfield_intervals:
        model.AddNoOverlap(subfield_intervals[sf])

def add_field_availability_constraints(model, interval_vars, assigned_fields, subfield_availability, global_time_slots):
    """
    Adds constraints to ensure that fields are only used when they are available.
    """
    idx_to_time = {idx: (day, t) for idx, (day, t) in enumerate(global_time_slots)}
    num_global_slots = len(global_time_slots)

    for team_name in interval_vars:
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
            for session_idx, session in enumerate(sessions):
                assigned_combo_var = session['assigned_combo']
                combo_indices = session['combo_indices']

                length = session['length']
                start_var = session['start']

                allowed_assignments = []

                for combo, combo_index in combo_indices.items():
                    for s in range(num_global_slots - length + 1):
                        is_available = True
                        for t in range(length):
                            global_t = s + t
                            if global_t >= num_global_slots:
                                is_available = False
                                break
                            day, time_idx = idx_to_time[global_t]
                            for field in combo:
                                if not subfield_availability[field][day][time_idx]:
                                    is_available = False
                                    break
                            if not is_available:
                                break
                        if is_available:
                            allowed_assignments.append([combo_index, s])

                model.AddAllowedAssignments([assigned_combo_var, start_var], allowed_assignments)

def add_team_day_constraints(model, interval_vars):
    """
    Adds AllDifferent constraints for day variables to ensure that each team does not have sessions on the same day.
    """
    for team_name in interval_vars:
        team_day_vars = []
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
            for session in sessions:
                team_day_vars.append(session['day_var'])
        model.AddAllDifferent(team_day_vars)

def add_allowed_assignments_constraints(model, interval_vars):
    """
    Adds allowed assignments constraints for start times and days.
    """
    for team_name in interval_vars:
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
            for session in sessions:
                day_var = session['day_var']
                start_var = session['start']
                allowed_assignments = session.get('allowed_assignments', [])
                if allowed_assignments:
                    model.AddAllowedAssignments([day_var, start_var], allowed_assignments)
