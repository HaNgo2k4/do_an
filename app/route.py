from fastapi import APIRouter, UploadFile, File, Query
from pathlib import Path
from fastapi.responses import JSONResponse
from app.model import RequestState
from agents.ai_agents import get_response_from_ai_agent
from audio_processing.speech_text import WavSpeechRecognizer
from agents.memory import get_dialogue_by_sessionId
from audio_processing.extract_music_segments import separate_speech_music

import json

router = APIRouter()

@router.post("/chat")
def chat_endpoint(request: RequestState, session_id: str = Query(...)):
    response = get_response_from_ai_agent(
        # llm_id="llama-3.3-70b-versatile",
        llm_id="llama-3.1-8b-instant",
        query=request.messages,
        provider=request.model_provider,
        user_id=session_id
    )
    return response

UPLOAD_DIR = Path("AudioFiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    name_parts = file.filename.split(".")
    subfolder = ".".join(name_parts[:-1])  # tên thư mục con bạn muốn thêm
    target_dir = UPLOAD_DIR / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    
    return {
        "status": "success",
        "file": str(file_path)
    }

@router.get("/get-audio-result")
async def get_audio_result(session_id: str = Query(...)):

    target_dir = UPLOAD_DIR / session_id
    if not target_dir.exists():
        return {"status": "error", "message": "Thư mục file không tồn tại"}

    file_path = target_dir / f"{session_id}.wav"
    if not file_path.exists():
        return {"status": "error", "message": "File không tồn tại"}

   
    result = separate_speech_music(file_path)

    speech_path = Path(result["speech"]) if result["speech"] else None
    nonspeech_path = Path(result["nonspeech"]) if result["nonspeech"] else None
    print(speech_path)
    print(nonspeech_path)

    # --- Xử lý speech (giọng nói / hát) ---
    text = ""
    if speech_path and speech_path.exists() and speech_path.stat().st_size > 0:
        recognizer = WavSpeechRecognizer()
        speech_results = recognizer.recognize_wav(str(speech_path))
        if not speech_results:
            text = ""
        elif speech_results[0].get("error"):
            text = "Nhận diện thất bại"
        else:
            text = speech_results[0]["text"]

    # --- Xử lý nonspeech (nhạc nền) ---
    has_music = False
    if nonspeech_path and nonspeech_path.exists():
        if nonspeech_path.stat().st_size < 1024:
            print(f"⚠️ File nonspeech rỗng: {nonspeech_path}")
        else:
            has_music = True
            if not text or text == "Nhận diện thất bại":
                text = "Nhận diện nhạc qua microphone"
    print(has_music)
    # --- Gửi vào AI agent ---
    response = get_response_from_ai_agent(
        llm_id="llama-3.3-70b-versatile",
        query=text,
        provider="Groq",
        user_id=session_id,
        has_wav=has_music
    )

    data = [
        {"role": "user", "content": text},
        {
            "role": "ai",
            "content": response["ai"],
            "tool": response.get("tool", [])
        }
    ]
    return data

@router.get("/get-dialogue/{session_id}")
def get_dialogue(session_id: str):
    dialogue = get_dialogue_by_sessionId(session_id)
    return JSONResponse(content=dialogue)