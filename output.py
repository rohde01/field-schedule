# output.py

def get_field_to_smallest_subfields(fields):
    """
    Creates a mapping from each field to its smallest subfields.
    """
    field_to_smallest_subfields = {}
    smallest_subfields_set = set()

    # Collect all field definitions
    field_defs = {}

    for field in fields:
        field_defs[field['name']] = field

        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                field_defs[quarter['name']] = quarter

        if 'half_subfields' in field:
            for half in field['half_subfields']:
                field_defs[half['name']] = half

    # Recursive function to get smallest subfields
    def get_smallest_subfields(field_name):
        field = field_defs[field_name]

        if 'quarter_subfields' in field:
            # Quarter subfields are the smallest subfields
            smallest = [quarter['name'] for quarter in field['quarter_subfields']]
            for name in smallest:
                smallest_subfields_set.add(name)
            return smallest

        elif 'fields' in field:
            # This field contains other fields
            smallest = []
            for subfield_name in field['fields']:
                smallest.extend(get_smallest_subfields(subfield_name))
            return smallest

        elif 'half_subfields' in field:
            # The field has half subfields
            smallest = []
            for half in field['half_subfields']:
                smallest.extend(get_smallest_subfields(half['name']))
            return smallest

        else:
            # No subfields, this is a smallest subfield
            smallest_subfields_set.add(field_name)
            return [field_name]

    # Build mapping
    for field_name in field_defs:
        field_to_smallest_subfields[field_name] = get_smallest_subfields(field_name)

    smallest_subfields_list = sorted(smallest_subfields_set)
    return field_to_smallest_subfields, smallest_subfields_list

from tabulate import tabulate

def print_solution(solver, teams, time_slots, x_vars, field_to_smallest_subfields, smallest_subfields_list):
    """
    Prints the solution in a visually pleasing format using the smallest subfields.
    """
    # Prepare mapping from smallest subfields to indices
    sf_indices = {sf: idx for idx, sf in enumerate(smallest_subfields_list)}

    for day in time_slots:
        print(f"\nDay: {day}\n")

        data = []
        subfields_labels = smallest_subfields_list

        for t, slot_time in enumerate(time_slots[day]):
            assignments = [''] * len(smallest_subfields_list)
            for team in teams:
                team_name = team['name']
                for idx in x_vars[team_name]:
                    for combo, var in x_vars[team_name][idx][day][t].items():
                        if solver.Value(var) == 1:
                            for field in combo:
                                smallest_subfields = field_to_smallest_subfields[field]
                                for sf in smallest_subfields:
                                    idx_sf = sf_indices[sf]
                                    assignments[idx_sf] = team_name

            row = [slot_time] + assignments
            data.append(row)

        headers = ["Time"] + subfields_labels
        table = tabulate(data, headers=headers, tablefmt="fancy_grid")
        print(table)
