"""
Filename: output.py
Output module for the scheduling problem.

Contains functions to process and display the solution in a readable format.
"""

from tabulate import tabulate
from utils import get_subfield_areas

def get_field_to_smallest_subfields(fields):
    """
    Creates a mapping from each field to its smallest subfields.
    """
    subfield_areas = get_subfield_areas(fields)
    field_to_smallest_subfields = {}
    smallest_subfields_set = set()

    for field_name, areas in subfield_areas.items():
        # Get the smallest subfields by finding areas that aren't subdivided further
        smallest = [area for area in areas if len(subfield_areas[area]) == 1]
        field_to_smallest_subfields[field_name] = smallest
        smallest_subfields_set.update(smallest)

    smallest_subfields_list = sorted(smallest_subfields_set)
    return field_to_smallest_subfields, smallest_subfields_list

def print_solution(solver, teams, time_slots, interval_vars, field_to_smallest_subfields, smallest_subfields_list, global_time_slots):
    """
    Prints the solution in a tabulated format.
    """
    sf_indices = {sf: idx for idx, sf in enumerate(smallest_subfields_list)}
    idx_to_time = {idx: (day, t) for idx, (day, t) in enumerate(global_time_slots)}

    for day in time_slots:
        print(f"\nDay: {day}\n")

        data = []
        subfields_labels = smallest_subfields_list

        num_slots_day = len(time_slots[day])

        for t in range(num_slots_day):
            assignments = [''] * len(smallest_subfields_list)
            global_t = None
            for idx, (d, time_idx) in idx_to_time.items():
                if d == day and time_idx == t:
                    global_t = idx
                    break
            if global_t is None:
                continue
            slot_time = time_slots[day][t]

            for team in teams:
                team_name = team['name']
                for idx_constraint in interval_vars[team_name]:
                    sessions = interval_vars[team_name][idx_constraint]
                    for session_idx, session in enumerate(sessions):
                        # Handle each part of the session
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

def print_raw_solution(solver, teams, interval_vars, field_name_to_id):
    """
    Prints raw solution values: team_id, team name, start index, end index, assigned field name, and field_id.
    """
    for team in teams:
        team_name = team['name']
        team_id = team['team_id']
        for idx_constraint in interval_vars[team_name]:
            sessions = interval_vars[team_name][idx_constraint]
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
