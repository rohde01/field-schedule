from fastapi import APIRouter, HTTPException
from database.fields import get_fields, create_field
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/fields",
    tags=["fields"]
)

class FieldCreate(BaseModel):
    facility_id: int
    name: str = Field(min_length=1, max_length=255)
    size: Literal['11v11', '8v8', '5v5', '3v3']
    field_type: Literal['full', 'half', 'quarter']
    parent_field_id: Optional[int] = None

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

@router.post("")
async def create_new_field(field: FieldCreate) -> dict:
    try:
        new_field = create_field(
            facility_id=field.facility_id,
            name=field.name,
            size=field.size,
            field_type=field.field_type,
            parent_field_id=field.parent_field_id
        )
        return {
            "field_id": new_field.field_id,
            "name": new_field.name,
            "size": new_field.size,
            "field_type": new_field.field_type,
            "parent_field_id": new_field.parent_field_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))