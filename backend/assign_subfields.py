from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List, Optional
from typing import Literal
from dataclass import Field
from utils import SIZE_TO_CAPACITY, time_str_to_block

def get_all_blocked_ids(field: Field, required_size: int, assigned_subfield_id: Optional[int] = None) -> set[int]:
    """
    Return the set of all field_ids that become blocked when assigning this session.
    For example:
      - If required_size == 1000 (full 11v11), block the entire field + all subfields.
      - If required_size == 500 (half 11v11), block the entire field + that half-field + its quarter subfields.
      - If required_size == 250 (quarter 11v11), block the entire field + the half that quarter belongs to + that quarter itself.
      - And similarly for 8v8, 5v5, etc.
    
    assigned_subfield_id can be:
      - The parent field_id itself (e.g. 11v11) if we decide to use the whole field
      - A half subfield_id
      - A quarter subfield_id
      - None if the size matches the parent (like 8v8 used at 500 = entire field anyway)
    """
    blocked_ids = set()
    
    # 1) Always block the parent field itself
    #    We'll climb the hierarchy up from assigned_subfield_id
    #    or just block the direct field if assigned_subfield_id is None
    def climb_parents(f: Field, target_id: int, blocked: set[int]):
        """ Recursively add field_id, and parent_field_id, until no parent. """
        blocked.add(target_id)
        if target_id != f.field_id:
            # If the assigned subfield is not the top-most field,
            # we need to find the actual field instance that has target_id
            # and climb from there.
            subfield_lookup = {}
            
            def index_fields(field: Field):
                subfield_lookup[field.field_id] = field
                for sf in field.quarter_subfields:
                    index_fields(sf)
                for sf in field.half_subfields:
                    index_fields(sf)
            
            index_fields(f)
            
            # climb up the chain
            current = subfield_lookup[target_id]
            while current is not None:
                blocked.add(current.field_id)
                if current.parent_field_id is None:
                    break
                current = subfield_lookup.get(current.parent_field_id)
        else:
            blocked.add(f.field_id)
    
    # 2) If the assigned field is the entire top-level field, block everything
    if required_size == 1000 and field.size == '11v11':
        # Full field
        blocked_ids.add(field.field_id)
        # Block all halves and quarters
        def block_recursively(f: Field):
            blocked_ids.add(f.field_id)
            for sf in f.half_subfields:
                block_recursively(sf)
            for sf in f.quarter_subfields:
                block_recursively(sf)
        block_recursively(field)
        return blocked_ids
    
    # For 8v8 used fully (500), 5v5 used fully (250), 3v3 used fully (125), 
    # or any "exact match" usage => top-level field is blocked
    # This also needs to block all subfields of that top-level field
    # in case an 8v8 is subdivided, etc.
    top_level_capacity = SIZE_TO_CAPACITY[field.size]
    if required_size == top_level_capacity:
        # The usage is for the entire top-level field (whatever that size is).
        def block_recursively(f: Field):
            blocked_ids.add(f.field_id)
            for sf in f.half_subfields:
                block_recursively(sf)
            for sf in f.quarter_subfields:
                block_recursively(sf)
        block_recursively(field)
        return blocked_ids
    
    # Otherwise, we're using subfields
    # We find the subfield by assigned_subfield_id (if not given, it might be the field itself).
    # Then we'll block that subfield, its parent chain, and any sub-subfields if needed.
    if assigned_subfield_id is None:
        # If for some reason we didn't pass in a subfield ID, block the top field anyway
        # (Should not generally happen, but fallback)
        blocked_ids.add(field.field_id)
        return blocked_ids
    
    # We do have a subfield in mind => climb parents, then block that subfield's own sub-subfields if needed.
    def index_all_subfields(f: Field) -> dict[int, Field]:
        d = {f.field_id: f}
        for half_sf in f.half_subfields:
            d.update(index_all_subfields(half_sf))
        for quart_sf in f.quarter_subfields:
            d.update(index_all_subfields(quart_sf))
        return d

    lookup = index_all_subfields(field)
    subfield_obj = lookup[assigned_subfield_id]
    
    # Climb up the parent chain
    climb_parents(field, assigned_subfield_id, blocked_ids)
    
    # Also block all sub-subfields belonging to the assigned subfield
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
    Post-process to assign specific subfields to sessions scheduled on the same top-level field and day.
    Modifies the sessions in-place to add subfield assignments.
    
    The corrected logic also ensures that a half-field assignment blocks
    all quarter-fields within that half (and the top-level field, to prevent
    someone else from assigning the full field in the same time range), etc.
    """
    if not field.half_subfields and not field.quarter_subfields:
        # No subfields to assign; the entire field is used as-is
        return

    # Sort sessions by start time to process them in chronological order
    day_sessions.sort(key=lambda x: (x['start_time'], x['end_time']))
    
    # Track usage over time: (start_block, end_block) -> set of blocked field_ids
    # so if a session overlaps in time and tries to use any of those blocked field_ids, it's a conflict
    subfield_usage = {}  # (start_block, end_block) -> set[int]
    
    for session in day_sessions:
        start_block = time_str_to_block(session['start_time'])
        end_block = time_str_to_block(session['end_time'])
        required_size = session['required_size']
        
        # Determine which intervals we overlap with
        overlapping_blocked = set()
        for (used_start, used_end), blocked_ids in subfield_usage.items():
            # Check time overlap
            if not (end_block <= used_start or start_block >= used_end):
                # There's an overlap in time => gather the blocked field_ids
                overlapping_blocked |= blocked_ids
        
        # Now choose how to assign the session's subfield usage
        # We do this by checking required_size and seeing if we have a valid subfield that isn't in overlapping_blocked
        assigned_subfield_id = None
        
        # === 11v11 logic
        if required_size == 1000 and field.size == '11v11':
            # Full field
            assigned_subfield_id = field.field_id
        elif required_size == 500 and field.size == '11v11':
            # Need a half subfield
            # Filter out half subfields that are already blocked
            possible_halves = [
                half_f.field_id
                for half_f in field.half_subfields
                if half_f.field_id not in overlapping_blocked
            ]
            if possible_halves:
                assigned_subfield_id = possible_halves[0]  # pick the first available
            else:
                # Could not find a free half => warning (the solver gave us a time, but it conflicts in post-processing)
                print(f"Warning: Could not find an available half subfield for session {session}")
                # We'll still assign the first half for debugging or remain unassigned
        elif required_size == 250 and field.size == '11v11':
            # Need a quarter subfield
            possible_quarters = [
                qf.field_id
                for qf in field.quarter_subfields
                if qf.field_id not in overlapping_blocked
            ]
            if possible_quarters:
                assigned_subfield_id = possible_quarters[0]
            else:
                print(f"Warning: Could not find an available quarter subfield for session {session}")
        
        # === 8v8 logic
        elif required_size == 500 and field.size == '8v8':
            # entire 8v8 field (no sub-subfields exist for "500" demand)
            assigned_subfield_id = field.field_id
        elif required_size == 250 and field.size == '8v8':
            # half of 8v8
            possible_halves = [
                half_f.field_id
                for half_f in field.half_subfields
                if half_f.field_id not in overlapping_blocked
            ]
            if possible_halves:
                assigned_subfield_id = possible_halves[0]
            else:
                print(f"Warning: Could not find half subfield for 8v8 {session}")
        elif required_size == 125 and field.size == '8v8':
            # quarter of 8v8
            possible_quarters = [
                qf.field_id
                for qf in field.quarter_subfields
                if qf.field_id not in overlapping_blocked
            ]
            if possible_quarters:
                assigned_subfield_id = possible_quarters[0]
            else:
                print(f"Warning: Could not find quarter subfield for 8v8 {session}")
        
        # === 5v5 logic
        elif required_size == 250 and field.size == '5v5':
            # entire 5v5 field
            assigned_subfield_id = field.field_id
        elif required_size == 125 and field.size == '5v5':
            # half of 5v5
            possible_halves = [
                hf.field_id
                for hf in field.half_subfields
                if hf.field_id not in overlapping_blocked
            ]
            if possible_halves:
                assigned_subfield_id = possible_halves[0]
            else:
                print(f"Warning: Could not find half subfield for 5v5 {session}")
        
        # === 3v3 logic
        elif required_size == 125 and field.size == '3v3':
            # entire 3v3 field
            assigned_subfield_id = field.field_id
        
        # If the assigned_subfield_id is still None but the solver scheduled it, 
        # that indicates a post-processing conflict. We'll just keep the top-level field in that scenario.
        if assigned_subfield_id is None:
            assigned_subfield_id = field.field_id
        
        # Update the session to hold the final field ID (subfield or entire field)
        session['field_id'] = assigned_subfield_id
        
        # Compute which IDs get blocked by this usage
        blocked_ids = get_all_blocked_ids(field, required_size, assigned_subfield_id)
        
        # Update subfield_usage for this time range
        # We merge with any existing usage for (start_block, end_block) if they are identical blocks
        # or store in a new entry if no exact match. 
        # 
        # NOTE: It's simpler to store usage in discrete intervals, but if you want to allow
        # partial overlaps, you'd need a more advanced structure. For typical scheduling, 
        # discrete intervals suffice.
        if (start_block, end_block) not in subfield_usage:
            subfield_usage[(start_block, end_block)] = set()
        subfield_usage[(start_block, end_block)].update(blocked_ids)
        
def post_process_solution(solution: List[dict], fields: List[Field]) -> List[dict]:
    """
    Post-process the entire solution to assign specific subfields.
    """
    # Create field lookup
    field_lookup = {f.field_id: f for f in fields}
    
    # Group sessions by field and day
    field_day_sessions = defaultdict(lambda: defaultdict(list))
    for session in solution:
        field_id = session['field_id']
        day = session['day_of_week']
        # Add required_size based on team capacity
        session['required_size'] = int(session.get('required_size', 1000))  # Default to full field if not specified
        field_day_sessions[field_id][day].append(session)
    
    # Process each field's sessions
    for field_id, day_sessions in field_day_sessions.items():
        field = field_lookup[field_id]
        for day, sessions in day_sessions.items():
            assign_subfields(field, sessions)
    
    # Flatten the processed solution
    processed_solution = []
    for field_sessions in field_day_sessions.values():
        for day_sessions in field_sessions.values():
            processed_solution.extend(day_sessions)
    
    return processed_solution