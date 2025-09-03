from fastapi import APIRouter, UploadFile, File, Query
from pathlib import Path
from fastapi.responses import JSONResponse
from app.model import RequestState
from agents.ai_agents import get_response_from_ai_agent
from agents.speech_text import WavSpeechRecognizer
from agents.memory import get_dialogue_by_sessionId
import json

router = APIRouter()

@router.post("/chat")
def chat_endpoint(request: RequestState, session_id: str = Query(...)):
    response = get_response_from_ai_agent(
        llm_id="llama-3.3-70b-versatile",
        # llm_id="llama-3.1-8b-instant",
        query=request.messages,
        provider=request.model_provider,
        user_id=session_id
    )
    return response

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {
        "status": "success",
        "file": str(file_path)
    }

@router.get("/get-audio-result")
async def get_audio_result(session_id: str = Query(...)):

    filename = session_id + ".wav"
    file_path = UPLOAD_DIR / filename
    recognizer = WavSpeechRecognizer()

    if not file_path.exists():
        return {"status": "error", "message": "File không tồn tại"}

    results = recognizer.recognize_wav(str(file_path))
    if not results or results[0].get("error"):
        return {"status": "error", "message": "Không hiểu âm thanh"}

    return {
        "status": "success",
        "file": filename,
        "results": results
    }

@router.get("/get-dialogue/{session_id}")
def get_dialogue(session_id: str):
    dialogue = get_dialogue_by_sessionId(session_id)
    return JSONResponse(content=dialogue)