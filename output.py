"""
Filename: output.py
Output module for the scheduling problem.

Contains functions to process and display the solution in a readable format.
"""

from tabulate import tabulate

def get_field_to_smallest_subfields(fields):
    """
    Creates a mapping from each field to its smallest subfields.
    """
    field_to_smallest_subfields = {}
    smallest_subfields_set = set()

    field_defs = {}

    for field in fields:
        field_defs[field['name']] = field

        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                field_defs[quarter['name']] = quarter

        if 'half_subfields' in field:
            for half in field['half_subfields']:
                field_defs[half['name']] = half

    def get_smallest_subfields(field_name):
        field = field_defs[field_name]

        if 'quarter_subfields' in field:
            smallest = [quarter['name'] for quarter in field['quarter_subfields']]
            for name in smallest:
                smallest_subfields_set.add(name)
            return smallest

        elif 'fields' in field:
            smallest = []
            for subfield_name in field['fields']:
                smallest.extend(get_smallest_subfields(subfield_name))
            return smallest

        elif 'half_subfields' in field:
            smallest = []
            for half in field['half_subfields']:
                smallest.extend(get_smallest_subfields(half['name']))
            return smallest

        else:
            smallest_subfields_set.add(field_name)
            return [field_name]

    for field_name in field_defs:
        field_to_smallest_subfields[field_name] = get_smallest_subfields(field_name)

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
                        start = solver.Value(session['start'])
                        end = solver.Value(session['end'])
                        assigned_combo_idx = solver.Value(session['assigned_combo'])
                        assigned_combo = session['possible_combos'][assigned_combo_idx]

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
