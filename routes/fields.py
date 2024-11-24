
from fastapi import APIRouter, HTTPException
from database.fields import get_fields
from typing import List

router = APIRouter(
    prefix="/fields",
    tags=["fields"]
)

@router.get("/facility/{facility_id}")
async def get_facility_fields(facility_id: int) -> List[dict]:
    fields = get_fields(facility_id)
    if not fields:
        raise HTTPException(status_code=404, detail="No fields found for this facility")
    return [
        {
            "field_id": field.field_id,
            "name": field.name,
            "size": field.size,
            "field_type": field.field_type,
            "parent_field_id": field.parent_field_id,
            "availability": field.availability,
            "quarter_subfields": [
                {"field_id": f.field_id, "name": f.name} for f in field.quarter_subfields
            ],
            "half_subfields": [
                {"field_id": f.field_id, "name": f.name} for f in field.half_subfields
            ]
        }
        for field in fields
    ]