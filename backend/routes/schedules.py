'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import logging
from backend.models.field import Field
from backend.models.constraint import Constraint

router = APIRouter(prefix="/schedules", tags=["schedules"])

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]

@router.post("/generate", response_model=dict)
async def generate_schedule_route(
    request: GenerateScheduleRequest
):
    try:
        logging.info(f"Received fields: {request.fields}")
        logging.info(f"Received constraints: {request.constraints}")
        
        return {"schedule_id": 123, "status": "success"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
