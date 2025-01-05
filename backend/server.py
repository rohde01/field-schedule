from fastapi import FastAPI
from routes.teams import router as teams_router
from routes.fields import router as fields_router
from routes.schedules import router as schedules_router
from routes.users import router as users_router
from routes.clubs import router as clubs_router
from routes.facilities import router as facilities_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(users_router)
app.include_router(clubs_router)
app.include_router(teams_router)
app.include_router(fields_router)
app.include_router(schedules_router)
app.include_router(facilities_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)