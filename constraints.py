"""
Filename: constraints.py
Constraint functions for the scheduling model.

Provides functions to add various constraints to the CP-SAT model to prevent overlapping sessions,
double booking, enforce field availability, and ensure sessions are on different days.
"""
from ortools.sat.python import cp_model
from collections import defaultdict
from typing import List, Dict, Any
from database.teams import Team


def add_no_overlapping_sessions_constraints(
    model: cp_model.CpModel,
    teams: List[Team],
    interval_vars: Dict[int, Any]
) -> None:
    """
    Adds constraints to prevent overlapping sessions for the same team.
    """
    for team in teams:
        team_id = team.team_id
        if team_id not in interval_vars:
            continue
        team_intervals = []
        for idx in interval_vars[team_id]:
            for session in interval_vars[team_id][idx]:
                team_intervals.extend(session['intervals'])
        model.AddNoOverlap(team_intervals)


def add_no_double_booking_constraints(
    model: cp_model.CpModel,
    teams: List[Team],
    interval_vars: Dict[int, Any],
    assigned_fields: Dict[int, Any],
    subfield_areas: Dict[str, List[str]],
    global_time_slots: List[Any]
) -> None:
    """
    Adds constraints to prevent double-booking of subfields.
    """
    subfield_intervals: Dict[str, List[Any]] = defaultdict(list)

    for team in teams:
        team_id = team.team_id
        if team_id not in interval_vars:
            continue
        for idx_constraint in interval_vars[team_id]:
            sessions = interval_vars[team_id][idx_constraint]
            for session_idx, session in enumerate(sessions):
                for part_idx, (interval, assigned_combo_var) in enumerate(zip(session['intervals'], session['assigned_combos'])):
                    combo_indices = session['combo_indices'][part_idx]
                    possible_combos = session['possible_combos'][part_idx]

                    for combo, combo_index in combo_indices.items():
                        subfields = set()
                        for field in combo:
                            subfields.update(subfield_areas[field])

                        uses_combo = model.NewBoolVar(f'uses_{team_id}_{idx_constraint}_{session_idx}_{part_idx}_{combo_index}')
                        model.Add(assigned_combo_var == combo_index).OnlyEnforceIf(uses_combo)
                        model.Add(assigned_combo_var != combo_index).OnlyEnforceIf(uses_combo.Not())

                        for sf in subfields:
                            sf_interval = model.NewOptionalIntervalVar(
                                interval.StartExpr(), interval.SizeExpr(), interval.EndExpr(), uses_combo,
                                f'sf_interval_{team_id}_{idx_constraint}_{session_idx}_{part_idx}_{sf}'
                            )
                            subfield_intervals[sf].append(sf_interval)

    for sf in subfield_intervals:
        model.AddNoOverlap(subfield_intervals[sf])


def add_field_availability_constraints(
    model: cp_model.CpModel,
    interval_vars: Dict[int, Any],
    assigned_fields: Dict[int, Any],
    subfield_availability: Dict[str, Dict[str, List[bool]]],
    global_time_slots: List[Any]
) -> None:
    """
    Adds constraints to ensure that fields are only used when they are available.
    """
    idx_to_time = {idx: (day, t) for idx, (day, t) in enumerate(global_time_slots)}
    num_global_slots = len(global_time_slots)

    for team_id in interval_vars:
        for idx_constraint in interval_vars[team_id]:
            sessions = interval_vars[team_id][idx_constraint]
            for session_idx, session in enumerate(sessions):
                for part_idx, (assigned_combo_var, length) in enumerate(zip(session['assigned_combos'], session['lengths'])):
                    combo_indices = session['combo_indices'][part_idx]
                    start_var = session['start_vars'][part_idx]

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


def add_team_day_constraints(
    model: cp_model.CpModel,
    interval_vars: Dict[int, Any]
) -> None:
    """
    Adds AllDifferent constraints for day variables to ensure that each team does not have sessions on the same day.
    """
    for team_id in interval_vars:
        team_day_vars = []
        for idx_constraint in interval_vars[team_id]:
            sessions = interval_vars[team_id][idx_constraint]
            for session in sessions:
                team_day_vars.append(session['day_var'])
        model.AddAllDifferent(team_day_vars)


def add_allowed_assignments_constraints(
    model: cp_model.CpModel,
    interval_vars: Dict[int, Any]
) -> None:
    """
    Adds allowed assignments constraints for start times and days.
    """
    for team_id in interval_vars:
        for idx_constraint in interval_vars[team_id]:
            sessions = interval_vars[team_id][idx_constraint]
            for session in sessions:
                day_var = session['day_var']
                start_var = session['start']
                allowed_assignments = session.get('allowed_assignments', [])
                if allowed_assignments:
                    if len(allowed_assignments) == 1:
                        model.Add(day_var == allowed_assignments[0][0])
                        model.Add(start_var == allowed_assignments[0][1])
                    else:
                        model.AddAllowedAssignments([day_var, start_var], allowed_assignments)
