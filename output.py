"""
Filename: output.py
Output module for the scheduling problem.

Contains functions to process and display the solution in a readable format.
"""

from tabulate import tabulate
from typing import List, Dict, Any, Tuple
from utils import get_field_to_smallest_subfields, build_time_slots, _build_time_slot_mappings
from .database.fields import get_fields, Field
from database.teams import get_teams, Team
from database.schedules import get_schedule_entries

def print_solution(solver: Any, teams: List[Team], time_slots: Dict[str, List[str]], interval_vars: Dict[int, Any], field_to_smallest_subfields: Dict[str, List[str]], smallest_subfields_list: List[str]) -> None:
    """
    Prints the solution in a tabulated format.
    """
    mappings = _build_time_slot_mappings(time_slots)
    global_time_slots = mappings['global_time_slots']
    idx_to_time = mappings['idx_to_time']
    day_to_global_indices = mappings['day_to_global_indices']
    sf_indices = {sf: idx for idx, sf in enumerate(smallest_subfields_list)}

    team_id_to_name = {team.team_id: team.name for team in teams}

    for day in time_slots:
        print(f"\nDay: {day}\n")
        data = []
        subfields_labels = smallest_subfields_list
        num_slots_day = len(time_slots[day])

        for t in range(num_slots_day):
            assignments = [''] * len(smallest_subfields_list)
            global_t = day_to_global_indices[day][t]
            slot_time = time_slots[day][t]

            for team in teams:
                team_id = team.team_id
                team_name = team.name
                if team_id not in interval_vars:
                    continue
                for idx_constraint in interval_vars[team_id]:
                    sessions = interval_vars[team_id][idx_constraint]
                    for session_idx, session in enumerate(sessions):
                        for part_idx, (interval, assigned_combo_var) in enumerate(zip(session['intervals'], session['assigned_combos'])):
                            start = solver.Value(session['start_vars'][part_idx])
                            end = solver.Value(session['end_vars'][part_idx])
                            assigned_combo_idx = solver.Value(assigned_combo_var)
                            assigned_combo = session['possible_combos'][part_idx][assigned_combo_idx]

                            if start <= global_t < end:
                                for field in assigned_combo:
                                    smallest_subfields = field_to_smallest_subfields[field]
                                    for sf in smallest_subfields:
                                        idx_sf = sf_indices[sf]
                                        assignments[idx_sf] = team_name
            row = [slot_time] + assignments
            data.append(row)

        headers = ["Time"] + subfields_labels
        table = tabulate(data, headers=headers, tablefmt="fancy_grid")
        print(table)

def print_raw_solution(solver: Any, teams: List[Team], interval_vars: Dict[int, Any], field_name_to_id: Dict[str, int]) -> None:
    """
    Prints raw solution values: team_id, team name, start index, end index, assigned field name, and field_id.
    """
    for team in teams:
        team_id = team.team_id
        team_name = team.name
        if team_id not in interval_vars:
            continue
        for idx_constraint in interval_vars[team_id]:
            sessions = interval_vars[team_id][idx_constraint]
            for session_idx, session in enumerate(sessions):
                for part_idx, (interval, assigned_combo_var) in enumerate(
                    zip(session['intervals'], session['assigned_combos'])
                ):
                    start_idx = solver.Value(session['start_vars'][part_idx])
                    end_idx = solver.Value(session['end_vars'][part_idx])
                    assigned_combo_idx = solver.Value(assigned_combo_var)
                    assigned_combo = session['possible_combos'][part_idx][assigned_combo_idx]
                    field_name = assigned_combo[0]
                    field_id = field_name_to_id.get(field_name, None)
                    print(f"{team_id},{team_name},{start_idx},{end_idx},{field_name},{field_id}")

def print_schedule_from_db(schedule_id: int) -> None:
    """
    Prints the schedule from the database for the given schedule_id in a tabulated format.
    """
    entries = get_schedule_entries(schedule_id)

    teams = get_teams()
    team_id_to_name = {team.team_id: team.name for team in teams}

    fields = get_fields()
    field_id_to_name: Dict[int, str] = {}
    field_name_to_field: Dict[str, Field] = {}
    for field in fields:
        field_id_to_name[field.field_id] = field.name
        field_name_to_field[field.name] = field
        for half_subfield in field.half_subfields:
            field_id_to_name[half_subfield.field_id] = half_subfield.name
            field_name_to_field[half_subfield.name] = half_subfield
        for quarter_subfield in field.quarter_subfields:
            field_id_to_name[quarter_subfield.field_id] = quarter_subfield.name
            field_name_to_field[quarter_subfield.name] = quarter_subfield

    time_slots, all_days = build_time_slots(fields)
    mappings = _build_time_slot_mappings(time_slots)
    idx_to_time = mappings['idx_to_time']
    day_to_global_indices = mappings['day_to_global_indices']

    field_to_smallest_subfields, smallest_subfields_list = get_field_to_smallest_subfields(fields)
    sf_indices = {sf: idx for idx, sf in enumerate(smallest_subfields_list)}

    field_id_to_smallest_subfields: Dict[int, List[str]] = {}
    for field_id, field_name in field_id_to_name.items():
        field = field_name_to_field[field_name]
        smallest_subfields = field_to_smallest_subfields.get(field_name, [field_name])
        field_id_to_smallest_subfields[field_id] = smallest_subfields

    assignments: Dict[Tuple[str, int, str], str] = {}
    for entry in entries:
        team_id, field_id, session_start, session_end, _ = entry
        team_name = team_id_to_name.get(team_id, f"Team {team_id}")
        field_name = field_id_to_name.get(field_id, f"Field {field_id}")
        smallest_subfields = field_id_to_smallest_subfields.get(field_id, [field_name])
        for global_t in range(session_start, session_end):
            day, t = idx_to_time[global_t]
            for sf in smallest_subfields:
                key = (day, t, sf)
                assignments[key] = team_name

    data_by_day: Dict[str, List[List[str]]] = {}
    for day in time_slots:
        data_by_day[day] = []

    for day in time_slots:
        num_slots_day = len(time_slots[day])
        for t in range(num_slots_day):
            slot_time = time_slots[day][t]
            row = [slot_time] + [''] * len(smallest_subfields_list)
            for idx_sf, sf in enumerate(smallest_subfields_list):
                key = (day, t, sf)
                team_name = assignments.get(key, '')
                row[idx_sf + 1] = team_name
            data_by_day[day].append(row)

    headers = ["Time"] + smallest_subfields_list
    for day in time_slots:
        print(f"\nDay: {day}\n")
        data = data_by_day[day]
        table = tabulate(data, headers=headers, tablefmt="fancy_grid")
        print(table)
