from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from video import router as video_router
import time

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
