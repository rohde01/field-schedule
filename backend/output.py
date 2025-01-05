"""
Filename: output.py
Output module for the scheduling problem.

Contains functions to process and display the solution in a readable format.
"""

from tabulate import tabulate
from typing import List, Dict, Any, Tuple
from utils import get_field_to_smallest_subfields, build_time_slots, _build_time_slot_mappings
from database.fields import get_fields, Field
from database.teams import get_teams, Team
from database.schedules import get_schedule_entries

def print_schedule_from_db(schedule_id: int, facility_id: int, club_id: int) -> None:
    """
    Prints the schedule from the database for the given schedule_id in a tabulated format.
    """
    entries = get_schedule_entries(schedule_id)

    teams = get_teams(club_id)
    team_id_to_name = {team.team_id: team.name for team in teams}

    fields = get_fields(facility_id)
    field_id_to_name: Dict[int, str] = {}
    field_name_to_field: Dict[str, Field] = {}
    
    for field in fields:  # Only process full fields as they now contain all subfields
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

if __name__ == "__main__":
    print_schedule_from_db(
        schedule_id=18,
        facility_id=1,
        club_id=1
    )
