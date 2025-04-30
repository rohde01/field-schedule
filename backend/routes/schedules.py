'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException
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

@router.post("/generate", response_model=List[ScheduleEntry])
async def generate_schedule_route(
    request: GenerateScheduleRequest
):
    try:
        print(f"[DEBUG] Received fields (count): {len(request.fields)}")
        print(f"[DEBUG] Received constraints (count): {len(request.constraints)}")
        print(f"[DEBUG] Received weekday_objective: {request.weekday_objective}")
        # call the generate_schedule function
        solution = generate_schedule(request)
        print(f"[DEBUG] Generated schedule solution: {solution}")
        if solution is None:
            raise HTTPException(status_code=400, detail="No feasible schedule found.")
        entries = convert_response_to_schedule_entries(solution)
        return entries
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print("[ERROR] Exception in generate_schedule_route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

