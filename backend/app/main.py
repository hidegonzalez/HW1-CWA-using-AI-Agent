from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import temperature, health
from .services.db_service import init_db

# Initialize DB for Phase 4 (History)
init_db()

app = FastAPI(title="Taiwan Weather Backend")

# Allow frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temperature.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "CWA Temperature API is running"}
