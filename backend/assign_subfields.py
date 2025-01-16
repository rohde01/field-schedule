from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List, Optional
from typing import Literal
from dataclass import Field
from utils import SIZE_TO_CAPACITY, time_str_to_block

def get_all_blocked_ids(field: Field, required_cost: int, assigned_subfield_id: Optional[int] = None) -> set[int]:
    """
    Return the set of all field_ids that become blocked when assigning this session.
    ...
    """
    blocked_ids = set()
    
    def climb_parents(f: Field, target_id: int, blocked: set[int]):
        blocked.add(target_id)
        if target_id != f.field_id:
            subfield_lookup = {}
            def index_fields(field: Field):
                subfield_lookup[field.field_id] = field
                for sf in field.quarter_subfields:
                    index_fields(sf)
                for sf in field.half_subfields:
                    index_fields(sf)
            index_fields(f)
            current = subfield_lookup[target_id]
            while current is not None:
                blocked.add(current.field_id)
                if current.parent_field_id is None:
                    break
                current = subfield_lookup.get(current.parent_field_id)
        else:
            blocked.add(f.field_id)
    
    # 2) If the assigned field is the entire top-level field, block everything
    if required_cost == 1000 and field.size == '11v11':
        def block_recursively(f: Field):
            blocked_ids.add(f.field_id)
            for sf in f.half_subfields:
                block_recursively(sf)
            for sf in f.quarter_subfields:
                block_recursively(sf)
        block_recursively(field)
        return blocked_ids
    
    # If cost equals the top-level capacity for the field, block the top field plus subfields
    top_level_capacity = SIZE_TO_CAPACITY[field.size]
    if required_cost == top_level_capacity:
        def block_recursively(f: Field):
            blocked_ids.add(f.field_id)
            for sf in f.half_subfields:
                block_recursively(sf)
            for sf in f.quarter_subfields:
                block_recursively(sf)
        block_recursively(field)
        return blocked_ids
    
    # Otherwise, handle partial usage
    if assigned_subfield_id is None:
        # fallback
        blocked_ids.add(field.field_id)
        return blocked_ids
    
    def index_all_subfields(f: Field) -> dict[int, Field]:
        d = {f.field_id: f}
        for half_sf in f.half_subfields:
            d.update(index_all_subfields(half_sf))
        for quart_sf in f.quarter_subfields:
            d.update(index_all_subfields(quart_sf))
        return d

    lookup = index_all_subfields(field)
    subfield_obj = lookup[assigned_subfield_id]
    
    climb_parents(field, assigned_subfield_id, blocked_ids)
    
    def block_descendants(fld: Field):
        blocked_ids.add(fld.field_id)
        for sf in fld.half_subfields:
            block_descendants(sf)
        for sf in fld.quarter_subfields:
            block_descendants(sf)
    
    block_descendants(subfield_obj)
    
    return blocked_ids

def assign_subfields(field: Field, day_sessions: List[dict]) -> None:
    """
    Post-process to assign specific subfields to sessions on the same top-level field + day.
    """
    if not field.half_subfields and not field.quarter_subfields:
        return

    # Sort sessions: required_field sessions first, then by time
    day_sessions.sort(key=lambda x: (
        0 if x.get('required_field') is not None else 1,
        x['start_time'],
        x['end_time']
    ))
    
    subfield_usage = {}

    for session in day_sessions:
        start_block = time_str_to_block(session['start_time'])
        end_block = time_str_to_block(session['end_time'])
        required_cost = session['required_cost']
        
        # Check for forced subfield assignment
        forced_subfield = session.get('required_field', None)
        
        overlapping_blocked = set()
        for (used_start, used_end), blocked_ids in subfield_usage.items():
            if not (end_block <= used_start or start_block >= used_end):
                overlapping_blocked |= blocked_ids

        assigned_subfield_id = None
        
        # Handle forced subfield if specified
        if forced_subfield is not None:
            if forced_subfield not in overlapping_blocked:
                assigned_subfield_id = forced_subfield
            else:
                raise ValueError(f"Forced subfield {forced_subfield} conflicts with existing assignments")
        
        # Only proceed with normal assignment logic if no forced subfield or if forced subfield was invalid
        if assigned_subfield_id is None:
            # 11v11 logic
            if required_cost == 1000 and field.size == '11v11':
                assigned_subfield_id = field.field_id
            elif required_cost == 500 and field.size == '11v11':
                possible_halves = [
                    half_f.field_id
                    for half_f in field.half_subfields
                    if half_f.field_id not in overlapping_blocked
                ]
                if possible_halves:
                    assigned_subfield_id = possible_halves[0]
            elif required_cost == 250 and field.size == '11v11':
                possible_quarters = [
                    qf.field_id
                    for qf in field.quarter_subfields
                    if qf.field_id not in overlapping_blocked
                ]
                if possible_quarters:
                    assigned_subfield_id = possible_quarters[0]

            # 8v8 logic
            elif required_cost == 500 and field.size == '8v8':
                assigned_subfield_id = field.field_id
            elif required_cost == 250 and field.size == '8v8':
                possible_halves = [
                    half_f.field_id
                    for half_f in field.half_subfields
                    if half_f.field_id not in overlapping_blocked
                ]
                if possible_halves:
                    assigned_subfield_id = possible_halves[0]
            elif required_cost == 125 and field.size == '8v8':
                possible_quarters = [
                    qf.field_id
                    for qf in field.quarter_subfields
                    if qf.field_id not in overlapping_blocked
                ]
                if possible_quarters:
                    assigned_subfield_id = possible_quarters[0]

            # 5v5 logic
            elif required_cost == 250 and field.size == '5v5':
                assigned_subfield_id = field.field_id
            elif required_cost == 125 and field.size == '5v5':
                possible_halves = [
                    hf.field_id
                    for hf in field.half_subfields
                    if hf.field_id not in overlapping_blocked
                ]
                if possible_halves:
                    assigned_subfield_id = possible_halves[0]

            # 3v3 logic
            elif required_cost == 125 and field.size == '3v3':
                assigned_subfield_id = field.field_id
        
        # If we still have not assigned, default to the top-level field
        if assigned_subfield_id is None:
            assigned_subfield_id = field.field_id
        
        session['field_id'] = assigned_subfield_id
        
        blocked_ids = get_all_blocked_ids(field, required_cost, assigned_subfield_id)
        
        if (start_block, end_block) not in subfield_usage:
            subfield_usage[(start_block, end_block)] = set()
        subfield_usage[(start_block, end_block)].update(blocked_ids)

def post_process_solution(solution: List[dict], fields: List[Field]) -> List[dict]:
    """
    Post-process the entire solution to assign specific subfields.
    """
    field_lookup = {f.field_id: f for f in fields}
    
    field_day_sessions = defaultdict(lambda: defaultdict(list))
    for session in solution:
        field_id = session['field_id']
        day = session['day_of_week']
        # 'required_cost' is already set, so we keep it
        field_day_sessions[field_id][day].append(session)
    
    for field_id, day_sessions in field_day_sessions.items():
        f = field_lookup[field_id]
        for day, sessions in day_sessions.items():
            assign_subfields(f, sessions)
    
    processed_solution = []
    for field_sessions in field_day_sessions.values():
        for day_sessions in field_sessions.values():
            processed_solution.extend(day_sessions)
    
    return processed_solution
