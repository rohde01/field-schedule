from models.field import Field
from models.schedule import Constraint
from typing import List, Dict, Tuple

SIZE_TO_CAPACITY = {
    '11v11': 1000,
    '8v8':   500,
    '5v5':   250,
    '3v3':   125,
}

def time_str_to_block(s: str) -> int:
    hh, mm = s.split(':')
    return int(hh)*4 + int(int(mm)//15)

def blocks_to_time_str(blocks: int) -> str:
    hh = blocks // 4
    mm = (blocks % 4) * 15
    return f"{hh:02d}:{mm:02d}"

def get_capacity_and_allowed(field: Field) -> tuple[int, List[int], int]:
    total_cap = SIZE_TO_CAPACITY[field.size]
    if field.quarter_subfields:
        max_splits = 4
    elif field.half_subfields:
        max_splits = 2
    else:
        max_splits = 1
    demands = {total_cap}
    if max_splits >= 2:
        demands.add(total_cap // 2)
    if max_splits >= 4:
        demands.add(total_cap // 4)
    allowed_demands = sorted(list(demands))
    return total_cap, allowed_demands, max_splits

def build_fields_by_id(top_fields: List[Field]) -> Tuple[Dict[int, Field], List[Field]]:
    """Build a dictionary mapping field IDs to field objects."""
    fields_by_id = {}
    
    def add_field_and_descendants(field: Field) -> None:
        fields_by_id[field.field_id] = field
        for hf in field.half_subfields:
            add_field_and_descendants(hf)
        for qf in field.quarter_subfields:
            add_field_and_descendants(qf)

    for tf in top_fields:
        add_field_and_descendants(tf)

    return fields_by_id, top_fields

def find_top_field_and_cost(subfield_id: int, fields_by_id: Dict[int, Field]) -> Tuple[int, int]:
    """
    Given a subfield_id, return (top_level_field_id, cost_for_subfield).
    cost_for_subfield is derived by dividing the top-level capacity 
    based on whether subfield is 'full', 'half', or 'quarter'.
    """
    if subfield_id not in fields_by_id:
        raise ValueError(f"Unknown required_field {subfield_id}")
    sf = fields_by_id[subfield_id]
    
    top_field = sf
    while top_field.parent_field_id is not None:
        top_field = fields_by_id[top_field.parent_field_id]

    top_capacity = SIZE_TO_CAPACITY[top_field.size]
    if sf.field_type == 'full':
        sub_cost = top_capacity
    elif sf.field_type == 'half':
        sub_cost = top_capacity // 2
    elif sf.field_type == 'quarter':
        sub_cost = top_capacity // 4
    else:
        sub_cost = top_capacity

    return (top_field.field_id, sub_cost)
