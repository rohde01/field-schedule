'''
Filename: fields.py in routes folder
'''

from fastapi import APIRouter, HTTPException
from database.fields import get_fields, create_field, add_field_availabilities, delete_field
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import logging
from datetime import time

# Add logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/fields",
    tags=["fields"]
)

class SubFieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    field_type: Literal['half', 'quarter']
    quarter_fields: Optional[List['SubFieldCreate']] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "Half Field A",
                "field_type": "half",
                "quarter_fields": [
                    {"name": "Quarter 1", "field_type": "quarter"}
                ]
            }
        }

class FieldCreate(BaseModel):
    facility_id: int
    name: str = Field(min_length=1, max_length=255)
    size: Literal['11v11', '8v8', '5v5', '3v3']
    field_type: Literal['full']
    half_fields: Optional[List[SubFieldCreate]] = []

    class Config:
        schema_extra = {
            "example": {
                "facility_id": 1,
                "name": "Main Field",
                "size": "11v11",
                "field_type": "full",
                "half_fields": []
            }
        }


class FieldAvailabilityBase(BaseModel):
    day_of_week: Literal['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_time: str
    end_time: str

class FieldAvailabilityCreate(BaseModel):
    availabilities: List[FieldAvailabilityBase]

    class Config:
        schema_extra = {
            "example": {
                "availabilities": [
                    {
                        "day_of_week": "Mon",
                        "start_time": "09:00",
                        "end_time": "17:00"
                    }
                ]
            }
        }

@router.get("/facility/{facility_id}")
async def get_facility_fields(facility_id: int) -> List[dict]:
    fields = get_fields(facility_id)
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
        # Add debug logging
        logger.debug(f"Received field data: {field.dict()}")
        
        # Create main field
        new_field = create_field(
            facility_id=field.facility_id,
            name=field.name,
            size=field.size,
            field_type=field.field_type
        )
        
        # Create half fields if any
        if field.half_fields:
            for half_field in field.half_fields:
                new_half = create_field(
                    facility_id=field.facility_id,
                    name=half_field.name,
                    size=field.size,
                    field_type='half',
                    parent_field_id=new_field.field_id
                )

                # Create quarter fields if any
                if half_field.quarter_fields:
                    for quarter_field in half_field.quarter_fields:
                        create_field(
                            facility_id=field.facility_id,
                            name=quarter_field.name,
                            size=field.size,
                            field_type='quarter',
                            parent_field_id=new_half.field_id
                        )

        return {"field_id": new_field.field_id}
    except Exception as e:
        logger.error(f"Error creating field: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{field_id}/availability")
async def add_field_availability(
    field_id: int,
    availability: FieldAvailabilityCreate
) -> dict:
    try:
        added = add_field_availabilities(field_id, availability.availabilities)
        return {"message": "Availability added successfully", "count": added}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{field_id}")
async def delete_field_endpoint(field_id: int) -> dict:
    try:
        result = delete_field(field_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting field: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))