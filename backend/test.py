# Test module for field conflict detection
from typing import List, Dict
from models.field import Field
from utils import time_str_to_block

def fieldConflicts(schedule: List[Dict], fields: List[Field]) -> None:
    # Build mapping of field_id to Field
    field_map = {f.field_id: f for f in fields}
    # Compute ancestors for each field
    ancestors = {f.field_id: set() for f in fields}
    for f in fields:
        cur = f
        while cur.parent_field_id is not None:
            ancestors[f.field_id].add(cur.parent_field_id)
            cur = field_map[cur.parent_field_id]

    # Convert schedule entries to blocks
    entries = []
    for sess in schedule:
        day = sess['day_of_week']
        s_blk = time_str_to_block(sess['start_time'])
        e_blk = time_str_to_block(sess['end_time'])
        entries.append((sess['session_id'], day, s_blk, e_blk, sess['field_id']))

    # Check each pair for direct conflicts
    for i in range(len(entries)):
        id1, day1, s1, e1, f1 = entries[i]
        for j in range(i+1, len(entries)):
            id2, day2, s2, e2, f2 = entries[j]
            if day1 != day2:
                continue
            if s1 < e2 and s2 < e1:
                # Same field
                if f1 == f2:
                    f_obj = field_map[f1]
                    print(f"Warning: Field '{f_obj.name}' (ID {f1}) is double booked in sessions {id1} and {id2}.")
                # Ancestor-descendant
                elif f1 in ancestors.get(f2, set()):
                    anc = field_map[f1]
                    desc = field_map[f2]
                    print(f"Warning: Cannot schedule {anc.field_type.value} '{anc.name}' (ID {f1}) and its subfield {desc.field_type.value} '{desc.name}' (ID {f2}) at the same time (sessions {id1}, {id2}).")
                elif f2 in ancestors.get(f1, set()):
                    anc = field_map[f2]
                    desc = field_map[f1]
                    print(f"Warning: Cannot schedule {anc.field_type.value} '{anc.name}' (ID {f2}) and its subfield {desc.field_type.value} '{desc.name}' (ID {f1}) at the same time (sessions {id2}, {id1}).")
