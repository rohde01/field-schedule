from pydantic import BaseModel

class Facility(BaseModel):
    facility_id: int
    club_id: int
    name: str
    is_primary: bool
