'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import logging
from models.field import Field
from models.constraint import Constraint

router = APIRouter(prefix="/schedules", tags=["schedules"])

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]
    weekday_objective: bool

@router.post("/generate", response_model=dict)
async def generate_schedule_route(
    request: GenerateScheduleRequest
):
    try:
        print(f"Received fields: {request.fields}")
        print(f"Received weekday_objective: {request.weekday_objective}")
        
        return {"schedule_id": 123, "status": "success"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
