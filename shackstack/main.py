from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shackstack.api.resources import router as resources_router

app = FastAPI(
    title="ShackStack",
    description="Decentralized infrastructure for secure community resource coordination",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resources_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "ShackStack API",
        "version": "0.1.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)