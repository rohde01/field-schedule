'''
Filename: fields.py in routes folder
'''
from fastapi import APIRouter, HTTPException, Depends
from database.fields import get_fields, create_field, add_field_availabilities, delete_field
from typing import List
from pydantic import Field
from dependencies.auth import get_current_user
from dependencies.permissions import validate_facility_access, validate_field_access, require_club_access
from backend.models.user import User
from database.fields import FieldAvailability, Field
from database.facilities import Facility

router = APIRouter(
    prefix="/fields",
    tags=["fields"]
)

@router.get("/facility/{facility_id}")
async def get_facility_fields(
    facility_id: int, 
    _: Facility = Depends(validate_facility_access),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    fields = get_fields(facility_id)
    return [
        {
            "field_id": field.field_id,
            "name": field.name,
            "size": field.size,
            "field_type": field.field_type,
            "parent_field_id": field.parent_field_id,
            "availability": field.availability,
            "is_active": field.is_active,
            "quarter_subfields": [
                {
                    "field_id": f.field_id,
                    "name": f.name,
                    "is_active": f.is_active,
                    "parent_field_id": f.parent_field_id
                } 
                for f in field.quarter_subfields
            ],
            "half_subfields": [
                {
                    "field_id": f.field_id,
                    "name": f.name,
                    "is_active": f.is_active,
                    "parent_field_id": f.parent_field_id
                } 
                for f in field.half_subfields
            ]
        }
        for field in fields
    ]

@router.get("/club/{club_id}")
async def get_club_fields(
    club_id: int,
    _: bool = Depends(require_club_access),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    fields = get_fields(club_id)  # Remove await since get_fields is synchronous
    return [
        {
            "field_id": field.field_id,
            "facility_id": field.facility_id,
            "name": field.name,
            "size": field.size,
            "field_type": field.field_type,
            "parent_field_id": field.parent_field_id,
            "availability": field.availability,
            "is_active": field.is_active,
            "quarter_subfields": [
                {
                    "field_id": f.field_id,
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "is_active": f.is_active,
                    "parent_field_id": f.parent_field_id
                } 
                for f in field.quarter_subfields
            ],
            "half_subfields": [
                {
                    "field_id": f.field_id,
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "is_active": f.is_active,
                    "parent_field_id": f.parent_field_id
                } 
                for f in field.half_subfields
            ]
        }
        for field in fields
    ]

@router.post("")
async def create_new_field(
    field: Field,
    current_user: User = Depends(get_current_user)
) -> dict:
    
    # Validate facility access first
    facility = await validate_facility_access(field.facility_id, current_user)
    
    try:      
        # Create main field
        new_field = create_field(
            facility_id=field.facility_id,
            name=field.name,
            size=field.size,
            field_type=field.field_type
        )
        
        if field.availabilities:
            add_field_availabilities(new_field.field_id, field.availabilities)
        
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
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{field_id}/availability")
async def add_field_availability(
    field_id: int,
    availability: FieldAvailability,
    facility: Facility = Depends(validate_field_access),
    current_user: User = Depends(get_current_user)
) -> dict:
    try:
        added = add_field_availabilities(field_id, availability.availabilities)
        return {"message": "Availability added successfully", "count": added}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{field_id}")
async def delete_field_endpoint(
    field_id: int, 
    facility: Facility = Depends(validate_field_access),
    current_user: User = Depends(get_current_user)
) -> dict:
    try:
        result = delete_field(field_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))