# Filename: utils.py
# Utility functions for the scheduling problem.

from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
from db import Field, get_fields, FieldAvailability, Constraint

def build_time_slots(fields: List[Field]) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Builds and returns a dictionary of time slots per day.
    """
    time_slots: Dict[str, List[str]] = {}
    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    available_days = {day for field in fields for day in field.availability}
    all_days = [day for day in day_order if day in available_days]
    for day in all_days:
        day_slots: Set[str] = set()
        for field in fields:
            if day in field.availability:
                start = field.availability[day].start_time
                end = field.availability[day].end_time
                total_start_minutes = parse_time_string(start, field.name, day)
                total_end_minutes = parse_time_string(end, field.name, day)
                field_time_slots = generate_time_slots_between(total_start_minutes, total_end_minutes, interval=15)
                day_slots.update(field_time_slots)
        time_slots[day] = sorted(day_slots)
    return time_slots, all_days

def _build_time_slot_mappings(time_slots: Dict[str, List[str]]) -> Dict[str, Any]:
    """Builds mappings from time slots to global indices and other related mappings."""
    global_time_slots: List[Tuple[str, int]] = []
    idx = 0
    idx_to_time: Dict[int, Tuple[str, int]] = {}
    idx_to_day: List[int] = []
    day_to_global_indices: Dict[str, List[int]] = defaultdict(list)
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

def get_subfields(fields: List[Field]) -> List[str]:
    """
    Returns a list of all subfields from all fields.
    """
    subfields = set()
    for field in fields:
        subfields.add(field.name)
        for half in field.half_subfields:
            subfields.add(half.name)
        for quarter in field.quarter_subfields:
            subfields.add(quarter.name)
    return list(subfields)

def get_field_to_smallest_subfields(fields: List[Field]) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Creates a mapping from each field to its smallest subfields.
    """
    subfield_areas = get_subfield_areas(fields)
    field_to_smallest_subfields: Dict[str, List[str]] = {}
    smallest_subfields_set = set()

    for field_name, areas in subfield_areas.items():
        # Get the smallest subfields by finding areas that aren't subdivided further
        smallest = [area for area in areas if len(subfield_areas[area]) == 1]
        field_to_smallest_subfields[field_name] = smallest
        smallest_subfields_set.update(smallest)

    smallest_subfields_list = sorted(smallest_subfields_set)
    return field_to_smallest_subfields, smallest_subfields_list

def parse_time_string(time_str: str, field_name: str = None, day: str = None) -> int:
    """Parses a time string 'HH:MM' and returns total minutes."""
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    except ValueError as e:
        if field_name and day:
            raise ValueError(f"Invalid time format in field '{field_name}' on day '{day}': {e}")
        else:
            raise ValueError(f"Invalid time format in time string '{time_str}': {e}")

def generate_time_slots_between(start_minutes: int, end_minutes: int, interval: int = 15) -> List[str]:
    """Generates time slots between start and end times at given interval in minutes."""
    num_intervals = (end_minutes - start_minutes) // interval
    return [
        f'{(start_minutes + i * interval) // 60}:{(start_minutes + i * interval) % 60:02d}'
        for i in range(num_intervals)
    ]

def get_subfield_areas(fields: List[Field]) -> Dict[str, List[str]]:
    """
    Returns a dictionary mapping each subfield to the areas it covers.
    """
    subfield_areas: Dict[str, List[str]] = {}
    for field in fields:
        field_name = field.name
        areas: List[str] = []
        if field.quarter_subfields:
            quarter_names = [quarter.name for quarter in field.quarter_subfields]
            areas.extend(quarter_names)
            for quarter in field.quarter_subfields:
                subfield_areas[quarter.name] = [quarter.name]
        elif field.half_subfields:
            half_names = [half.name for half in field.half_subfields]
            areas.extend(half_names)
            for half in field.half_subfields:
                subfield_areas[half.name] = [half.name]
        else:
            areas.append(field_name)
            subfield_areas[field_name] = [field_name]

        subfield_areas[field_name] = areas

        if field.half_subfields and field.quarter_subfields:
            for half in field.half_subfields:
                half_name = half.name
                half_fields = [quarter.name for quarter in half.quarter_subfields]
                subfield_areas[half_name] = half_fields

    return subfield_areas

def get_size_to_combos(fields: List[Field]) -> Dict[Tuple[str, str], List[Tuple[str]]]:
    """
    Returns a dictionary mapping (required_size, subfield_type) to possible field combinations.
    """
    size_to_combos: Dict[Tuple[str, str], List[Tuple[str]]] = {}
    for field in fields:
        field_size = field.size
        field_name = field.name
        combo_key = (field_size, 'full')
        size_to_combos.setdefault(combo_key, []).append((field_name,))
        if field.half_subfields:
            combo_key = (field_size, 'half')
            for half in field.half_subfields:
                half_name = half.name
                size_to_combos.setdefault(combo_key, []).append((half_name,))
        if field.quarter_subfields:
            combo_key = (field_size, 'quarter')
            for quarter in field.quarter_subfields:
                quarter_name = quarter.name
                size_to_combos.setdefault(combo_key, []).append((quarter_name,))
    return size_to_combos

def get_subfield_availability(fields: List[Field], time_slots: Dict[str, List[str]], all_subfields: List[str]) -> Dict[str, Dict[str, List[bool]]]:
    """
    Returns a dictionary indicating availability of each subfield per day per time slot.
    """
    subfield_availability: Dict[str, Dict[str, List[bool]]] = {sf: {day: [False]*len(time_slots[day]) for day in time_slots} for sf in all_subfields}

    for field in fields:
        field_name = field.name
        field_availability = field.availability
        field_subfields = [field_name]

        if field.half_subfields:
            field_subfields.extend([half.name for half in field.half_subfields])
        if field.quarter_subfields:
            field_subfields.extend([quarter.name for quarter in field.quarter_subfields])

        for day in time_slots:
            if day in field_availability:
                start_time = field_availability[day].start_time
                end_time = field_availability[day].end_time
                total_start_minutes = parse_time_string(start_time, field_name, day)
                total_end_minutes = parse_time_string(end_time, field_name, day)
                slot_times_minutes = [parse_time_string(slot_time) for slot_time in time_slots[day]]
                for t, slot_minutes in enumerate(slot_times_minutes):
                    if total_start_minutes <= slot_minutes < total_end_minutes:
                        for sf in field_subfields:
                            subfield_availability[sf][day][t] = True
    return subfield_availability

def get_cost_to_combos(fields: List[Field], field_costs: Dict[Tuple[str, str], int]) -> Dict[int, List[Tuple[str]]]:
    """
    Returns a dictionary mapping required_cost to possible field combinations.
    """
    cost_to_combos: Dict[int, List[Tuple[str]]] = defaultdict(list)
    for field in fields:
        field_name = field.name
        field_size = field.size
        cost_key = field_costs.get((field_size, 'full'))
        if cost_key is not None:
            cost_to_combos[cost_key].append((field_name,))
        if field.half_subfields:
            cost_key = field_costs.get((field_size, 'half'))
            for half in field.half_subfields:
                half_name = half.name
                if cost_key is not None:
                    cost_to_combos[cost_key].append((half_name,))
        if field.quarter_subfields:
            cost_key = field_costs.get((field_size, 'quarter'))
            for quarter in field.quarter_subfields:
                quarter_name = quarter.name
                if cost_key is not None:
                    cost_to_combos[cost_key].append((quarter_name,))
    return cost_to_combos

def get_field_costs() -> Dict[Tuple[str, str], int]:
    """Returns a dictionary mapping (field_size, subfield_type) to cost."""
    # Base costs for full-size fields
    base_costs = {
        '11v11': 1000,
        '8v8': 500,
        '5v5': 250,
        '3v3': 125
    }
    costs: Dict[Tuple[str, str], int] = {}
    fields = get_fields()
    field_sizes = {field.size for field in fields}

    for size in field_sizes:
        base_cost = base_costs.get(size, 0)
        costs[(size, 'full')] = base_cost

        if size in ['11v11', '8v8']:
            costs[(size, 'half')] = base_cost // 2
            costs[(size, 'quarter')] = base_cost // 4
        elif size == '5v5':
            costs[(size, 'half')] = base_cost // 2
    return costs

def _handle_start_time_constraint(constraint: Constraint, time_slots: Dict[str, List[str]], mappings: Dict[str, Any]) -> Tuple[List[List[int]], Set[int]]:
    """
    Helper function to handle start time constraints.
    Ensures that the entire session length fits within the day and field availability.
    """
    allowed_assignments: List[List[int]] = []
    allowed_start_times: Set[int] = set()

    specified_time = constraint.start_time
    length = constraint.length
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

def get_parent_field(subfield_name: str, fields: List[Field]) -> str:
    """
    Returns the parent field name for a given subfield name.
    """
    for field in fields:
        if subfield_name == field.name:
            return field.name
        for half in field.half_subfields:
            if subfield_name == half.name:
                return field.name
        for quarter in field.quarter_subfields:
            if subfield_name == quarter.name:
                return field.name
    raise ValueError(f"Parent field not found for subfield '{subfield_name}'")

def get_parent_field_ids(possible_combos: List[Tuple[str]], parent_field_name_to_id: Dict[str, int], fields: List[Field]) -> List[int]:
    """Returns a list of parent field IDs for the given possible combos."""
    parent_field_ids = []
    for combo in possible_combos:
        parent_field = get_parent_field(combo[0], fields)
        parent_field_id = parent_field_name_to_id[parent_field]
        parent_field_ids.append(parent_field_id)
    return parent_field_ids

def time_slots_to_minutes(time_slots: List[str]) -> List[int]:
    """Converts a list of time slot strings to total minutes."""
    return [parse_time_string(slot_time) for slot_time in time_slots]

def _get_allowed_assignments(constraint: Constraint, time_slots: Dict[str, List[str]], mappings: Dict[str, Any]) -> Tuple[List[List[int]], List[int]]:
    """
    Helper function to get allowed assignments and start times based on constraint and time slots.
    """
    day_to_global_indices = mappings['day_to_global_indices']
    day_name_to_index = mappings['day_name_to_index']
    if constraint.start_time:
        allowed_assignments, allowed_start_times_set = _handle_start_time_constraint(constraint, time_slots, mappings)
        allowed_start_times = sorted(allowed_start_times_set)  
    else:
        allowed_assignments: List[List[int]] = []
        allowed_start_times_set: Set[int] = set()
        total_length = constraint.length
        for day_name in time_slots:
            day_idx = day_name_to_index[day_name]
            day_global_indices = day_to_global_indices[day_name]
            num_slots_day = len(day_global_indices)
            for s_local in range(num_slots_day - total_length + 1):
                s_global = day_global_indices[s_local]
                allowed_assignments.append([day_idx, s_global])
                allowed_start_times_set.add(s_global)
        allowed_start_times = sorted(allowed_start_times_set)
    return allowed_assignments, allowed_start_times

def _get_possible_combos(constraint: Constraint, size_to_combos: Dict[Any, Any], cost_to_combos: Dict[int, List[Any]]) -> Tuple[List[Any], List[Any]]:
    """Determines possible field combinations based on constraint type."""
    if constraint.required_cost:
        required_cost = constraint.required_cost
        possible_combos_part1 = cost_to_combos.get(required_cost, [])
    else:
        key_part1 = (constraint.required_size, constraint.subfield_type)
        possible_combos_part1 = size_to_combos.get(key_part1, [])

    if constraint.partial_ses_time:
        if constraint.partial_ses_space_cost is not None:
            required_cost_part2 = constraint.partial_ses_space_cost
            possible_combos_part2 = cost_to_combos.get(required_cost_part2, [])
        elif constraint.partial_ses_space_size is not None:
            key_part2 = (constraint.required_size, constraint.partial_ses_space_size)
            possible_combos_part2 = size_to_combos.get(key_part2, [])
        else:
            possible_combos_part2 = possible_combos_part1
    else:
        possible_combos_part2 = possible_combos_part1

    return possible_combos_part1, possible_combos_part2
