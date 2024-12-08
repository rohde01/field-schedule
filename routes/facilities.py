
from fastapi import APIRouter, HTTPException
from database.facilities import create_facility, get_facilities
from typing import List, Optional
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/facilities",
    tags=["facilities"]
)

class FacilityCreate(BaseModel):
    club_id: int
    name: str = Field(min_length=1, max_length=255)
    is_primary: bool = False

@router.get("/club/{club_id}")
async def get_club_facilities(club_id: int) -> List[dict]:
    facilities = get_facilities(club_id)
    if not facilities:
        raise HTTPException(status_code=404, detail="No facilities found for this club")
    return [
        {
            "facility_id": facility.facility_id,
            "name": facility.name,
            "is_primary": facility.is_primary
        }
        for facility in facilities
    ]

@router.post("")
async def create_new_facility(facility: FacilityCreate) -> dict:
    try:
        new_facility = create_facility(
            club_id=facility.club_id,
            name=facility.name,
            is_primary=facility.is_primary
        )
        return {
            "facility_id": new_facility.facility_id,
            "name": new_facility.name,
            "is_primary": new_facility.is_primary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))