

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routes import router as v1_router
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Multimodal Gemini App",
    description="A FastAPI service for multimodal (text, image, audio) interactions via Google Gemini.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(v1_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """Health-check endpoint."""
    return {"status": "ok", "message": "Multimodal Gemini App is running."}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )
