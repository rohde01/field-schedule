"""
Filename: utils.py
Utility functions for the scheduling problem.

Contains helper functions for building time slots, subfield data, and availability mappings.
"""

from test_data import get_fields

def build_time_slots(fields):
    """
    Builds and returns a dictionary of time slots per day.
    """
    time_slots = {}
    # Define the correct order of days
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    available_days = {day for field in fields for day in field['availability']}
    # Sort all_days based on day_order
    all_days = [day for day in day_order if day in available_days]
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

def get_cost_to_combos(fields, field_costs):
    """
    Returns a dictionary mapping required_cost to possible field combinations.
    """
    from collections import defaultdict
    cost_to_combos = defaultdict(list)
    for field in fields:
        field_name = field['name']
        field_size = field['size']
        # Full field
        cost_key = field_costs.get((field_size, 'full'))
        if cost_key is not None:
            cost_to_combos[cost_key].append((field_name,))
        # Half subfields
        if 'half_subfields' in field:
            for half in field['half_subfields']:
                half_name = half['name']
                cost_key = field_costs.get((field_size, 'half'))
                if cost_key is not None:
                    cost_to_combos[cost_key].append((half_name,))
        # Quarter subfields
        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                quarter_name = quarter['name']
                cost_key = field_costs.get((field_size, 'quarter'))
                if cost_key is not None:
                    cost_to_combos[cost_key].append((quarter_name,))
    return cost_to_combos

def get_field_costs():
    """Returns a dictionary mapping (field_size, subfield_type) to cost."""
    # Base costs for full-size fields
    base_costs = {
        '11v11': 1000,
        '8v8': 500,
        '5v5': 250,
        '3v3': 125     
    }
    costs = {}
    # Get unique field sizes from get_fields()
    field_sizes = {field['size'] for field in get_fields()}
    
    # Calculate costs for each field size and its subdivisions
    for size in field_sizes:
        base_cost = base_costs[size]
        costs[(size, 'full')] = base_cost
        
        if size == '11v11' or size == '8v8':
            costs[(size, 'half')] = base_cost // 2
            costs[(size, 'quarter')] = base_cost // 4
        elif size == '5v5':
            costs[(size, 'half')] = base_cost // 2
    return costs

def _handle_start_time_constraint(constraint, time_slots, mappings):
    """
    Helper function to handle start time constraints.
    Ensures that the entire session length fits within the day and field availability.
    """
    allowed_assignments = []
    allowed_start_times = set()
    
    specified_time = constraint['start_time']
    length = constraint['length']
    time_matched = False
    
    for day_name in time_slots:
        day_slots = time_slots[day_name]
        day_global_indices = mappings['day_to_global_indices'][day_name]
        try:
            start_slot_idx = day_slots.index(specified_time)
        except ValueError:
            continue

        # Check if there are enough slots left in the day for the entire session
        if start_slot_idx + length <= len(day_slots):
            s_global = day_global_indices[start_slot_idx]
            allowed_assignments.append([mappings['day_name_to_index'][day_name], s_global])
            allowed_start_times.add(s_global)
            time_matched = True
    
    if not time_matched:
        raise ValueError(
            f"Specified start_time '{specified_time}' with length {length} " 
            "does not fit within available day slots"
        )
    
    return allowed_assignments, allowed_start_times

def get_parent_field(subfield_name):
    """
    Returns the parent field name for a given subfield name.
    """
    fields = get_fields()
    for field in fields:
        if subfield_name == field['name']:
            return field['name']
        if 'half_subfields' in field:
            for half in field['half_subfields']:
                if subfield_name == half['name']:
                    return field['name']
        if 'quarter_subfields' in field:
            for quarter in field['quarter_subfields']:
                if subfield_name == quarter['name']:
                    return field['name']
    raise ValueError(f"Parent field not found for subfield '{subfield_name}'")
