# filename: utils.py

def build_time_slots(fields):
    """
    Builds and returns a dictionary of time slots per day.

    Returns:
        time_slots (dict): Dictionary where keys are days and values are lists of time slots.
        all_days (list): Sorted list of all days.
    """
    time_slots = {}
    all_days = sorted({day for field in fields for day in field['availability']})
    for day in all_days:
        time_slots[day] = []
        for field in fields:
            if day in field['availability']:
                start = field['availability'][day]['start']
                end = field['availability'][day]['end']
                start_hour, start_minute = map(int, start.split(':'))
                end_hour, end_minute = map(int, end.split(':'))
                total_start_minutes = start_hour * 60 + start_minute
                total_end_minutes = end_hour * 60 + end_minute
                num_intervals = (total_end_minutes - total_start_minutes) // 15
                field_time_slots = [
                    f'{(total_start_minutes + i * 15) // 60}:{(total_start_minutes + i * 15) % 60:02d}'
                    for i in range(num_intervals)
                ]
                time_slots[day].extend(field_time_slots)
        time_slots[day] = sorted(set(time_slots[day]))
    return time_slots, all_days

pass


def get_subfields(fields):
    """
    Returns a list of all quarter subfields from all fields.
    """
    return [sf for field in fields for sf in field['quarter_subfields']]
pass

def get_size_to_combos(fields):
    """
    Returns a dictionary mapping required sizes to possible field combinations.
    """
    size_to_combos = {'quarter': [], 'half': [], 'full': []}
    for field in fields:
        size_to_combos['quarter'].extend([(sf,) for sf in field['quarter_subfields']])
        size_to_combos['half'].extend([tuple(combo) for combo in field['half_subfields']])
        size_to_combos['full'].append(tuple(field['quarter_subfields']))
    return size_to_combos
pass

def print_solution(solver, teams, time_slots, x_vars, all_subfields):
    """
    Prints the solution in a tabular format.
    """
    # Prepare mapping from subfields to indices
    sf_indices = {sf: idx for idx, sf in enumerate(all_subfields)}

    for day in time_slots:
        print(f"Day: {day}")
        header = "Timeslot\t" + "\t".join(all_subfields)
        print(header)
        for t, slot_time in enumerate(time_slots[day]):
            assignments = [''] * len(all_subfields)
            for team in teams:
                team_name = team['name']
                for idx in x_vars[team_name]:
                    for combo, var in x_vars[team_name][idx][day][t].items():
                        if solver.Value(var) == 1:
                            for sf in combo:
                                idx_sf = sf_indices[sf]
                                assignments[idx_sf] = team_name
            print(f'{slot_time}\t' + '\t'.join(assignments))
        print("\n")

def get_subfield_availability(fields, time_slots, all_subfields):
    """
    Returns a dictionary indicating availability of each subfield per day per time slot.
    """
    subfield_availability = {sf: {day: [False]*len(time_slots[day]) for day in time_slots} for sf in all_subfields}

    for field in fields:
        field_subfields = field['quarter_subfields']
        field_availability = field['availability']
        for day in time_slots:
            if day in field_availability:
                start_time = field_availability[day]['start']
                end_time = field_availability[day]['end']
                start_hour, start_minute = map(int, start_time.split(':'))
                end_hour, end_minute = map(int, end_time.split(':'))
                total_start_minutes = start_hour * 60 + start_minute
                total_end_minutes = end_hour * 60 + end_minute
                for t, slot_time in enumerate(time_slots[day]):
                    slot_hour, slot_minute = map(int, slot_time.split(':'))
                    slot_minutes = slot_hour * 60 + slot_minute
                    if total_start_minutes <= slot_minutes < total_end_minutes:
                        for sf in field_subfields:
                            subfield_availability[sf][day][t] = True
    return subfield_availability

