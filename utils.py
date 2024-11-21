"""
Filename: utils.py
Utility functions for the scheduling problem.

Contains helper functions for building time slots, subfield data, and availability mappings.
"""

from db import get_fields
from collections import defaultdict


def build_time_slots(fields):
    """
    Builds and returns a dictionary of time slots per day.
    """
    time_slots = {}
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    available_days = {day for field in fields for day in field['availability']}
    all_days = [day for day in day_order if day in available_days]
    for day in all_days:
        time_slots[day] = []
        for field in fields:
            if day in field['availability']:
                start = field['availability'][day]['start']
                end = field['availability'][day]['end']
                total_start_minutes = parse_time_string(start, field['name'], day)
                total_end_minutes = parse_time_string(end, field['name'], day)
                field_time_slots = generate_time_slots_between(total_start_minutes, total_end_minutes, interval=15)
                time_slots[day].extend(field_time_slots)
        time_slots[day] = sorted(set(time_slots[day]))
    return time_slots, all_days


def _build_time_slot_mappings(time_slots):
    """Builds mappings from time slots to global indices and other related mappings."""
    global_time_slots = []
    idx = 0
    idx_to_time = {}
    idx_to_day = []
    day_to_global_indices = defaultdict(list)
    day_names = list(time_slots.keys())
    day_name_to_index = {day_name: index for index, day_name in enumerate(day_names)}

    for day in time_slots:
        for t, slot_time in enumerate(time_slots[day]):
            idx_to_time[idx] = (day, t)
            global_time_slots.append((day, t))
            idx_to_day.append(day_name_to_index[day])
            day_to_global_indices[day].append(idx)
            idx += 1

    num_global_slots = idx

    return {
        'global_time_slots': global_time_slots,
        'idx_to_time': idx_to_time,
        'idx_to_day': idx_to_day,
        'day_to_global_indices': day_to_global_indices,
        'day_names': day_names,
        'day_name_to_index': day_name_to_index,
        'num_global_slots': num_global_slots
    }


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


def parse_time_string(time_str, field_name=None, day=None):
    """Parses a time string 'HH:MM' and returns total minutes."""
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    except ValueError as e:
        if field_name and day:
            raise ValueError(f"Invalid time format in field '{field_name}' on day '{day}': {e}")
        else:
            raise ValueError(f"Invalid time format in time string '{time_str}': {e}")


def generate_time_slots_between(start_minutes, end_minutes, interval=15):
    """Generates time slots between start and end times at given interval in minutes."""
    num_intervals = (end_minutes - start_minutes) // interval
    return [
        f'{(start_minutes + i * interval) // 60}:{(start_minutes + i * interval) % 60:02d}'
        for i in range(num_intervals)
    ]


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
                total_start_minutes = parse_time_string(start_time, field_name, day)
                total_end_minutes = parse_time_string(end_time, field_name, day)
                slot_times_minutes = [parse_time_string(slot_time) for slot_time in time_slots[day]]
                for t, slot_minutes in enumerate(slot_times_minutes):
                    if total_start_minutes <= slot_minutes < total_end_minutes:
                        for sf in field_subfields:
                            subfield_availability[sf][day][t] = True
    return subfield_availability


def get_cost_to_combos(fields, field_costs):
    """
    Returns a dictionary mapping required_cost to possible field combinations.
    """
    from collections import defaultdict
    cost_to_combos = defaultdict(list)
    for field in fields:
        field_name = field['name']
        field_size = field['size']
        cost_key = field_costs.get((field_size, 'full'))
        if cost_key is not None:
            cost_to_combos[cost_key].append((field_name,))
        if 'half_subfields' in field:
            for half in field['half_subfields']:
                half_name = half['name']
                cost_key = field_costs.get((field_size, 'half'))
                if cost_key is not None:
                    cost_to_combos[cost_key].append((half_name,))
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
    field_sizes = {field['size'] for field in get_fields()}

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


def get_parent_field_ids(possible_combos, parent_field_name_to_id):
    """Returns a list of parent field IDs for the given possible combos."""
    parent_field_ids = []
    for combo in possible_combos:
        parent_field = get_parent_field(combo[0])
        parent_field_id = parent_field_name_to_id[parent_field]
        parent_field_ids.append(parent_field_id)
    return parent_field_ids


def time_slots_to_minutes(time_slots):
    """Converts a list of time slot strings to total minutes."""
    return [parse_time_string(slot_time) for slot_time in time_slots]


def _get_allowed_assignments(constraint, time_slots, mappings):
    """
    Helper function to get allowed assignments and start times based on constraint and time slots.
    """
    day_to_global_indices = mappings['day_to_global_indices']
    day_name_to_index = mappings['day_name_to_index']
    if 'start_time' in constraint:
        allowed_assignments, allowed_start_times = _handle_start_time_constraint(constraint, time_slots, mappings)
    else:
        allowed_assignments = []
        allowed_start_times = set()
        total_length = constraint['length']
        for day_name in time_slots:
            day_idx = day_name_to_index[day_name]
            day_global_indices = day_to_global_indices[day_name]
            num_slots_day = len(day_global_indices)
            for s_local in range(num_slots_day - total_length + 1):
                s_global = day_global_indices[s_local]
                allowed_assignments.append([day_idx, s_global])
                allowed_start_times.add(s_global)
    allowed_start_times = sorted(allowed_start_times)
    return allowed_assignments, allowed_start_times


def _get_possible_combos(constraint, size_to_combos, cost_to_combos):
    """Determines possible field combinations based on constraint type."""
    if 'required_cost' in constraint:
        required_cost = constraint['required_cost']
        possible_combos_part1 = cost_to_combos.get(required_cost, [])
    else:
        key_part1 = (constraint['required_size'], constraint['subfield_type'])
        possible_combos_part1 = size_to_combos.get(key_part1, [])

    if 'partial_ses_time' in constraint:
        if 'partial_ses_space' in constraint:
            if 'required_cost' in constraint:
                required_cost_part2 = constraint['partial_ses_space']
                possible_combos_part2 = cost_to_combos.get(required_cost_part2, [])
            else:
                key_part2 = (constraint['required_size'], constraint['partial_ses_space'])
                possible_combos_part2 = size_to_combos.get(key_part2, [])
        else:
            possible_combos_part2 = possible_combos_part1
    else:
        possible_combos_part2 = possible_combos_part1

    return possible_combos_part1, possible_combos_part2