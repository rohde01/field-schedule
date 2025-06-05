'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Request
import traceback
from typing import List
from pydantic import BaseModel
from models.field import Field
from models.constraint import Constraint
from main import generate_schedule  # import solver function
from utils import convert_response_to_schedule_entries
from models.schedule import ScheduleEntry

router = APIRouter(prefix="/schedules", tags=["schedules"])

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]
    weekday_objective: bool
    start_time_objective: bool

class ScheduleResponse(BaseModel):
    entries: List[ScheduleEntry]
    message: str

@router.post("/generate", response_model=ScheduleResponse)
async def generate_schedule_route(
    request: GenerateScheduleRequest
):
    try:
        print(f"[DEBUG] Received fields (count): {len(request.fields)}")
        print(f"[DEBUG] Received constraints (count): {len(request.constraints)}")
        print(f"[DEBUG] Received weekday_objective: {request.weekday_objective}")
        print(f"[DEBUG] Received start_time_objective: {request.start_time_objective}")
        # call the generate_schedule function
        result = generate_schedule(request)
        if result is None:
            raise HTTPException(status_code=400, detail="No feasible schedule found.")
        
        entries = convert_response_to_schedule_entries(result["solution"])
        solution_type = result.get("solution_type", "UNKNOWN")
        message = f"Found a {solution_type} solution!"
        
        return ScheduleResponse(entries=entries, message=message)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print("[ERROR] Exception in generate_schedule_route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

