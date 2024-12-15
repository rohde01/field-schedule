import logging
from fastapi import APIRouter, HTTPException, Depends
from database.facilities import (
    create_facility, get_facilities, Facility,
    FacilityError, DuplicatePrimaryFacilityError, DuplicateFacilityNameError
)
from typing import List, Optional
from pydantic import BaseModel, Field
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access, validate_facility_access
from models.users import User

router = APIRouter(
    prefix="/facilities",
    tags=["facilities"]
)

logger = logging.getLogger(__name__)

class FacilityCreate(BaseModel):
    club_id: int
    name: str = Field(min_length=1, max_length=255)
    is_primary: bool = False

@router.get("/club/{club_id}")
async def get_club_facilities(
    club_id: int,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(require_club_access)
) -> List[dict]:
    # First, validate club access
    await require_club_access(club_id)(current_user)
    
    logger.info(f"Fetching facilities for club_id={club_id}")
    logger.info(f"Request made by user_id={current_user.user_id}")
    
    try:
        facilities = get_facilities(club_id)
        logger.info(f"Found {len(facilities)} facilities for club_id={club_id}")
        
        if not facilities:
            logger.warning(f"No facilities found for club_id={club_id}")
            raise HTTPException(status_code=404, detail="No facilities found for this club")
        
        return [
            {
                "facility_id": facility.facility_id,
                "name": facility.name,
                "is_primary": facility.is_primary
            }
            for facility in facilities
        ]
    except Exception as e:
        logger.error(f"Error fetching facilities: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching facilities")

@router.post("")
async def create_new_facility(
    facility_create: FacilityCreate,
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
        logger.error(f"Unexpected error creating facility: {str(e)}")
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