from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from src.services.whisper_service import whisper_service
from src.schemas.transcribe_schemas import (
    TranscriptionRequest,
    TranscriptionResponse,
    TranscriptionProgress,
    WhisperModel,
    TranscriptionAction,
    ErrorResponse,
)
from src.core.config import settings
import os
import tempfile
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload_audio", response_model=TranscriptionResponse)
async def upload_audio(
    file: UploadFile = File(...),
    model: str = Form(default="turbo"),
    action: str = Form(default="transcribe"),
    language: str = Form(default=None),
):
    """Upload and transcribe audio file"""

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Check file size
    file_size = 0
    temp_path = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            suffix=file_extension, delete=False
        ) as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            file_size = len(content)

            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB",
                )

            temp_file.write(content)

        # Validate model and action
        try:
            whisper_model = WhisperModel(model)
            transcription_action = TranscriptionAction(action)
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid parameter: {str(e)}"
            )

        # Perform transcription
        text, detected_language, processing_time = (
            whisper_service.transcribe_audio(
                temp_path, whisper_model, transcription_action, language
            )
        )

        return TranscriptionResponse(
            success=True,
            text=text,
            language=detected_language,
            processing_time=processing_time,
            model_used=model,
            action_performed=action,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing audio: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.websocket("/transcribe_stream")
async def transcribe_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time audio transcription"""
    await websocket.accept()

    try:
        # Get initial configuration
        config_data = await websocket.receive_text()
        config = json.loads(config_data)

        model = WhisperModel(config.get("model", "turbo"))
        action = TranscriptionAction(config.get("action", "transcribe"))

        logger.info(
            f"Starting real-time transcription with model: {model}, action: {action}"
        )

        chunk_counter = 0

        while True:
            try:
                # Receive audio data
                data = await websocket.receive_bytes()
                chunk_counter += 1

                # Process audio chunk
                if len(data) > 0:
                    # Send progress update
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "progress",
                                "chunk_id": chunk_counter,
                                "status": "processing",
                            }
                        )
                    )

                    # Transcribe chunk
                    text = whisper_service.transcribe_audio_chunk(
                        data, model, action
                    )

                    if text:
                        # Send transcription result
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "transcription",
                                    "chunk_id": chunk_counter,
                                    "text": text,
                                    "model": model.value,
                                    "action": action.value,
                                }
                            )
                        )

                    # Send completion status
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "progress",
                                "chunk_id": chunk_counter,
                                "status": "completed",
                            }
                        )
                    )

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Error in real-time transcription: {str(e)}")
                await websocket.send_text(
                    json.dumps({"type": "error", "message": str(e)})
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during setup")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@router.get("/models")
async def get_available_models():
    """Get list of available Whisper models"""
    return {
        "models": [model.value for model in WhisperModel],
        "default": settings.DEFAULT_WHISPER_MODEL,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SafeSound API"}
