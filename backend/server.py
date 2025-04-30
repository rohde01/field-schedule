from fastapi import FastAPI
from routes.schedules import router as schedules_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Field Schedule API"}

app.include_router(schedules_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)