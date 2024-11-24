from fastapi import FastAPI
from routes.teams import router as teams_router
from routes.fields import router as fields_router

app = FastAPI()
app.include_router(teams_router)
app.include_router(fields_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)