import logging
from fastapi import Depends, HTTPException, status
from models.users import User
from database.users import user_belongs_to_club
from database.facilities import get_facility
from .auth import get_current_user 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_club_access(club_id: int):
    """
    Factory function that returns a dependency to ensure the current user 
    belongs to the specified club.
    """
    async def club_access_dependency(current_user: User = Depends(get_current_user)):
        logger.info(f"Checking club access for user_id={current_user.user_id} club_id={club_id}")
        has_access = user_belongs_to_club(current_user.user_id, club_id)
        logger.info(f"Access check result: {has_access}")
        
        if not has_access:
            logger.warning(f"Access denied for user_id={current_user.user_id} to club_id={club_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this club."
            )
        logger.info(f"Access granted for user_id={current_user.user_id} to club_id={club_id}")
        return True
    return club_access_dependency

def require_facility_access(club_id: int):
    """
    Factory function that returns a dependency to ensure the current user 
    belongs to the specified club that owns the facility.
    """
    async def facility_access_dependency(current_user: User = Depends(get_current_user)):
        if not user_belongs_to_club(current_user.user_id, club_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this facility."
            )
        return True
    return facility_access_dependency

async def validate_facility_access(facility_id: int, current_user: User = Depends(get_current_user)):
    """
    Dependency to validate facility access based on the facility ID
    """
    facility = get_facility(facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    if not user_belongs_to_club(current_user.user_id, facility.club_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this facility"
        )
    return facility
