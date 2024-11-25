'''
Filename: server.py
Discription: This file is the main entry point for the FastAPI application. It includes the routes for teams, fields, and schedules.
'''

from fastapi import FastAPI
from routes.teams import router as teams_router
from routes.fields import router as fields_router
from routes.schedules import router as schedules_router

app = FastAPI()
app.include_router(teams_router)
app.include_router(fields_router)
app.include_router(schedules_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)