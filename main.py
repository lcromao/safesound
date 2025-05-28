from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.routes import transcribe
from src.core.config import settings
import uvicorn

app = FastAPI(
    title="SafeSound - Audio Transcription App",
    description="A complete audio transcription application using OpenAI Whisper",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="src/templates")

# Include routers
app.include_router(transcribe.router, prefix="/api")

# Root endpoint to serve the main page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
