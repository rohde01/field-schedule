'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
import traceback
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from models.field import Field
from models.constraint import Constraint
from main import generate_schedule  # import solver function
from utils import convert_response_to_schedule_entries
from models.schedule import ScheduleEntry
import threading
from datetime import datetime

router = APIRouter(prefix="/schedules", tags=["schedules"])

# In-memory job storage (in production, use Redis or database)
job_storage: Dict[str, Dict[str, Any]] = {}
job_lock = threading.Lock()

class GenerateScheduleRequest(BaseModel):
    fields: List[Field]
    constraints: List[Constraint]
    weekday_objective: bool
    start_time_objective: bool

class ScheduleResponse(BaseModel):
    entries: List[ScheduleEntry]
    message: str

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    result: Optional[ScheduleResponse] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

def background_generate_schedule(job_id: str, request: GenerateScheduleRequest):
    """Background task to generate schedule"""
    with job_lock:
        job_storage[job_id]["status"] = "running"
    # define callback to capture intermediate solutions
    def partial_callback(solution):
        print(f"[DEBUG] Job {job_id}: Received intermediate solution with {len(solution)} sessions")
        entries = convert_response_to_schedule_entries(solution)
        with job_lock:
            job_storage[job_id]["result"] = ScheduleResponse(entries=entries, message="Intermediate solution")

    try:
        print(f"[DEBUG] Job {job_id}: Starting schedule generation")
        print(f"[DEBUG] Job {job_id}: Fields count: {len(request.fields)}")
        print(f"[DEBUG] Job {job_id}: Constraints count: {len(request.constraints)}")
        print(f"[DEBUG] Job {job_id}: Weekday objective: {request.weekday_objective}")
        print(f"[DEBUG] Job {job_id}: Start time objective: {request.start_time_objective}")
        
        # Call the generate_schedule function
        result = generate_schedule(request, solution_callback=partial_callback)
        
        if result is None:
            with job_lock:
                job_storage[job_id]["status"] = "failed"
                job_storage[job_id]["error"] = "No feasible schedule found."
                job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()
            return
        
        entries = convert_response_to_schedule_entries(result["solution"])
        solution_type = result.get("solution_type", "UNKNOWN")
        message = f"Found a {solution_type} solution!"
        
        schedule_response = ScheduleResponse(entries=entries, message=message)
        
        with job_lock:
            job_storage[job_id]["status"] = "completed"
            job_storage[job_id]["result"] = schedule_response
            job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
        print(f"[DEBUG] Job {job_id}: Schedule generation completed successfully")
        
    except ValueError as ve:
        with job_lock:
            job_storage[job_id]["status"] = "failed"
            job_storage[job_id]["error"] = str(ve)
            job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()
        print(f"[ERROR] Job {job_id}: ValueError: {ve}")
    except Exception as e:
        with job_lock:
            job_storage[job_id]["status"] = "failed"
            job_storage[job_id]["error"] = str(e)
            job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()
        print(f"[ERROR] Job {job_id}: Exception in background_generate_schedule:")
        traceback.print_exc()

@router.post("/generate", response_model=JobResponse)
async def generate_schedule_route(
    request: GenerateScheduleRequest,
    background_tasks: BackgroundTasks
):
    """Start schedule generation as background job"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job in storage
        with job_lock:
            job_storage[job_id] = {
                "status": "pending",
                "result": None,
                "error": None,
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": None
            }
        
        # Add background task
        background_tasks.add_task(background_generate_schedule, job_id, request)
        
        print(f"[DEBUG] Created job {job_id} for schedule generation")
        
        return JobResponse(job_id=job_id, status="pending")
        
    except Exception as e:
        print("[ERROR] Exception in generate_schedule_route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get status of a schedule generation job"""
    with job_lock:
        job_data = job_storage.get(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_data["status"],
        result=job_data["result"],
        error=job_data["error"],
        created_at=job_data["created_at"],
        completed_at=job_data["completed_at"]
    )

