from fastapi import APIRouter, HTTPException, Depends
from database.facilities import (
    create_facility, get_facilities,
    FacilityError, DuplicatePrimaryFacilityError, DuplicateFacilityNameError
)
from typing import List
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access, validate_facility_access
from models.user import User
from models.facility import Facility

router = APIRouter(
    prefix="/facilities",
    tags=["facilities"]
)


@router.get("/club/{club_id}")
async def get_club_facilities(
    club_id: int,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(require_club_access)
) -> List[dict]:
    # First, validate club access
    await require_club_access(club_id)(current_user)
    
    try:
        facilities = get_facilities(club_id)
        
        if not facilities:
            return []
        
        return [
            {
                "facility_id": facility.facility_id,
                "name": facility.name,
                "is_primary": facility.is_primary
            }
            for facility in facilities
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching facilities")

@router.post("")
async def create_new_facility(
    facility_create: Facility,
    current_user: User = Depends(get_current_user),
) -> dict:
    # Validate club access
    await require_club_access(facility_create.club_id)(current_user)
    
    try:
        new_facility = create_facility(
            club_id=facility_create.club_id,
            name=facility_create.name,
            is_primary=facility_create.is_primary
        )
        return {
            "facility_id": new_facility.facility_id,
            "name": new_facility.name,
            "is_primary": new_facility.is_primary
        }
    except DuplicatePrimaryFacilityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateFacilityNameError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FacilityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{facility_id}")
async def get_facility_by_id(
    facility_id: int,
    facility: Facility = Depends(validate_facility_access)
) -> dict:
    return {
        "facility_id": facility.facility_id,
        "name": facility.name,
        "is_primary": facility.is_primary,
        "club_id": facility.club_id
    }