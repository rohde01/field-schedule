def build_time_slots(fields):
    """
    Builds and returns a dictionary of time slots per day.

    Returns:
        time_slots (dict): Dictionary where keys are days and values are lists of time slots.
        all_days (list): Sorted list of all days.
    """
    all_days = sorted({day for field in fields for day in field['availability']})
    time_slots = {}
    for day in all_days:
        field_times = [
            (field['availability'][day]['start'], field['availability'][day]['end'])
            for field in fields if day in field['availability']
        ]
        if field_times:
            earliest_start = min(start for start, _ in field_times)
            latest_end = max(end for _, end in field_times)
            start_hour, start_minute = map(int, earliest_start.split(':'))
            end_hour, end_minute = map(int, latest_end.split(':'))
            total_start_minutes = start_hour * 60 + start_minute
            total_end_minutes = end_hour * 60 + end_minute
            num_intervals = (total_end_minutes - total_start_minutes) // 15
            time_slots[day] = [
                f'{(total_start_minutes + i*15)//60}:{(total_start_minutes + i*15)%60:02d}' for i in range(num_intervals)
            ]
        else:
            time_slots[day] = []
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
                for combo, var in x_vars[team_name][day][t].items():
                    if solver.Value(var) == 1:
                        for sf in combo:
                            idx = sf_indices[sf]
                            assignments[idx] = team_name
            print(f'{slot_time}\t' + '\t'.join(assignments))
        print("\n")
pass