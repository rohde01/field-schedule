"""
Filename: utils.py
Utility functions for the scheduling problem.

Contains helper functions for building time slots, subfield data, and availability mappings.
"""

def build_time_slots(fields):
    """
    Builds and returns a dictionary of time slots per day.
    """
    time_slots = {}
    all_days = sorted({day for field in fields for day in field['availability']})
    for day in all_days:
        time_slots[day] = []
        for field in fields:
            if day in field['availability']:
                start = field['availability'][day]['start']
                end = field['availability'][day]['end']
                try:
                    start_hour, start_minute = map(int, start.split(':'))
                    end_hour, end_minute = map(int, end.split(':'))
                except ValueError as e:
                    raise ValueError(f"Invalid time format in field '{field['name']}' on day '{day}': {e}")
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

def get_subfields(fields):
    """
    Returns a list of all subfields from all fields.
    """
    subfields = set()
    for field in fields:
        field_name = field['name']
        subfields.add(field_name)
        if 'half_subfields' in field:
            for half in field['half_subfields']:
                subfields.add(half['name'])
        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                subfields.add(quarter['name'])
    return list(subfields)

def get_size_to_combos(fields):
    """
    Returns a dictionary mapping (required_size, subfield_type) to possible field combinations.
    """
    size_to_combos = {}
    for field in fields:
        field_size = field['size']
        field_name = field['name']
        combo_key = (field_size, 'full')
        size_to_combos.setdefault(combo_key, []).append((field_name,))
        if 'half_subfields' in field:
            for half in field['half_subfields']:
                half_name = half['name']
                combo_key = (field_size, 'half')
                size_to_combos.setdefault(combo_key, []).append((half_name,))
        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                quarter_name = quarter['name']
                combo_key = (field_size, 'quarter')
                size_to_combos.setdefault(combo_key, []).append((quarter_name,))
    return size_to_combos

def get_subfield_availability(fields, time_slots, all_subfields):
    """
    Returns a dictionary indicating availability of each subfield per day per time slot.
    """
    subfield_availability = {sf: {day: [False]*len(time_slots[day]) for day in time_slots} for sf in all_subfields}

    for field in fields:
        field_name = field['name']
        field_availability = field['availability']
        field_subfields = [field_name]

        if 'half_subfields' in field:
            for half in field['half_subfields']:
                field_subfields.append(half['name'])
        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                field_subfields.append(quarter['name'])

        for day in time_slots:
            if day in field_availability:
                start_time = field_availability[day]['start']
                end_time = field_availability[day]['end']
                try:
                    start_hour, start_minute = map(int, start_time.split(':'))
                    end_hour, end_minute = map(int, end_time.split(':'))
                except ValueError as e:
                    raise ValueError(f"Invalid time format in field '{field_name}' on day '{day}': {e}")
                total_start_minutes = start_hour * 60 + start_minute
                total_end_minutes = end_hour * 60 + end_minute
                for t, slot_time in enumerate(time_slots[day]):
                    slot_hour, slot_minute = map(int, slot_time.split(':'))
                    slot_minutes = slot_hour * 60 + slot_minute
                    if total_start_minutes <= slot_minutes < total_end_minutes:
                        for sf in field_subfields:
                            subfield_availability[sf][day][t] = True
    return subfield_availability

def get_subfield_areas(fields):
    """
    Returns a dictionary mapping each subfield to the areas it covers.
    """
    subfield_areas = {}
    for field in fields:
        field_name = field['name']
        areas = []
        if 'quarter_subfields' in field:
            quarter_names = [quarter['name'] for quarter in field['quarter_subfields']]
            areas.extend(quarter_names)
            for quarter in field['quarter_subfields']:
                subfield_areas[quarter['name']] = [quarter['name']]
        elif 'half_subfields' in field:
            half_names = [half['name'] for half in field['half_subfields']]
            areas.extend(half_names)
            for half in field['half_subfields']:
                subfield_areas[half['name']] = [half['name']]
        else:
            areas.append(field_name)
            subfield_areas[field_name] = [field_name]

        subfield_areas[field_name] = areas

        if 'half_subfields' in field and 'quarter_subfields' in field:
            for half in field['half_subfields']:
                half_name = half['name']
                half_fields = half['fields']
                subfield_areas[half_name] = half_fields

    return subfield_areas
