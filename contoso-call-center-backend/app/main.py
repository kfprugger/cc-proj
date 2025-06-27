from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import psycopg
import time
import random
import base64
from typing import Dict, List
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

from .models import (
    CallGenerationRequest, 
    CallGenerationResponse, 
    GeneratedCall, 
    TranscriptData,
    ScenarioType,
    SentimentType,
    DurationType
)
from .services import TranscriptGenerator, AudioGenerator, SyntheticDataGenerator

app = FastAPI(
    title="Contoso Call Center Synthetic Generator API",
    description="API for generating synthetic call center transcripts and audio files",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

transcript_generator = TranscriptGenerator()
audio_generator = AudioGenerator()
data_generator = SyntheticDataGenerator()

generated_calls_storage: Dict[str, List[GeneratedCall]] = {}
in_memory_transcripts: Dict[str, str] = {}
in_memory_audio: Dict[str, bytes] = {}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "Contoso Call Center Synthetic Generator API",
        "version": "1.0.0",
        "disclaimer": "All generated data is synthetic and fictitious. This application is for simulation purposes only and does not contain real PHI or PII data."
    }

@app.post("/generate-calls", response_model=CallGenerationResponse)
async def generate_calls(request: CallGenerationRequest):
    """Generate synthetic call center transcripts and audio files."""
    
    if not request.scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario must be selected")
    
    if request.num_calls < 1 or request.num_calls > 50:
        raise HTTPException(status_code=400, detail="Number of calls must be between 1 and 50")
    
    start_time = time.time()
    generated_calls = []
    session_id = str(uuid.uuid4())
    
    try:
        scenarios_list = [s.value for s in request.scenarios]
        scenario_distribution = []
        
        for i in range(request.num_calls):
            scenario_distribution.append(scenarios_list[i % len(scenarios_list)])
        
        random.shuffle(scenario_distribution)
        
        for i in range(request.num_calls):
            scenario = scenario_distribution[i]
            
            transcript_data = transcript_generator.generate_transcript(
                scenario=scenario,
                sentiment=request.sentiment.value,
                duration=request.duration.value
            )
            
            transcript_model = TranscriptData(**transcript_data)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            transcript_id = f"contoso_call_{timestamp}_call_{i+1}"
            transcript_result = transcript_generator.save_transcript_to_file(
                transcript_data, 
                transcript_id, 
                save_locally=request.save_transcripts_locally
            )
            
            if request.save_transcripts_locally and transcript_result['file_path']:
                transcript_file_url = f"/transcript/{transcript_id}"
            else:
                in_memory_transcripts[transcript_id] = transcript_result['content']
                transcript_file_url = f"/transcript/{transcript_id}"
            
            audio_file_url = None
            if request.audio_settings.generate_audio:
                audio_settings = {
                    'sampling_rate': request.audio_settings.sampling_rate,
                    'channels': request.audio_settings.channels
                }
                audio_id = f"contoso_call_{timestamp}_call_{i+1}"
                audio_result = audio_generator.generate_audio(
                    transcript_data['transcript'],
                    audio_settings,
                    audio_id,
                    save_locally=request.audio_settings.save_audio_locally
                )
                
                if audio_result:
                    if isinstance(audio_result, str) and os.path.exists(audio_result):
                        audio_file_url = f"/audio/{audio_id}"
                    elif isinstance(audio_result, bytes):
                        in_memory_audio[audio_id] = audio_result
                        audio_file_url = f"/audio/{audio_id}"
            
            generated_call = GeneratedCall(
                id=i + 1,
                scenario=scenario,
                transcript_data=transcript_model,
                audio_file_url=audio_file_url,
                transcript_file_url=transcript_file_url
            )
            
            generated_calls.append(generated_call)
        
        generated_calls_storage[session_id] = generated_calls
        
        generation_time = time.time() - start_time
        
        return CallGenerationResponse(
            calls=generated_calls,
            total_calls=len(generated_calls),
            generation_time=round(generation_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating calls: {str(e)}")

@app.get("/audio/{audio_id}")
async def get_audio_file(audio_id: str):
    """Retrieve generated audio file from disk or memory."""
    from fastapi.responses import FileResponse
    import os
    
    audio_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_audio')
    file_path = os.path.join(audio_dir, f"{audio_id}.wav")
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            filename=f"{audio_id}.wav"
        )
    
    if audio_id in in_memory_audio:
        return Response(
            content=in_memory_audio[audio_id],
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={audio_id}.wav"}
        )
    
    raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/transcript/{transcript_id}")
async def get_transcript_file(transcript_id: str):
    """Retrieve generated transcript file from disk or memory."""
    from fastapi.responses import FileResponse
    import os
    
    transcript_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_transcripts')
    file_path = os.path.join(transcript_dir, f"{transcript_id}.txt")
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="text/plain",
            filename=f"{transcript_id}.txt"
        )
    
    if transcript_id in in_memory_transcripts:
        return Response(
            content=in_memory_transcripts[transcript_id],
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={transcript_id}.txt"}
        )
    
    raise HTTPException(status_code=404, detail="Transcript file not found")

@app.get("/scenarios")
async def get_available_scenarios():
    """Get list of available call scenarios."""
    return {
        "scenarios": [
            {
                "id": "healthcare_provider",
                "name": "Healthcare Provider Inquiry",
                "description": "Healthcare provider inquiring about a past patient encounter"
            },
            {
                "id": "patient_visit", 
                "name": "Patient Visit Inquiry",
                "description": "Patient calling about a recent visit to a hospital, clinic, or emergency room"
            },
            {
                "id": "caregiver_inquiry",
                "name": "Caregiver Inquiry", 
                "description": "Caregiver calling with a medical question about a patient under Contoso Medical's care"
            }
        ]
    }

@app.get("/audio-settings")
async def get_audio_settings():
    """Get available audio configuration options."""
    return {
        "sampling_rates": [8000, 16000, 32000, 48000],
        "channels": [
            {"value": 1, "name": "Mono (Recommended)"},
            {"value": 2, "name": "Stereo"}
        ],
        "specifications": {
            "format": "WAV (Microsoft PCM)",
            "bit_depth": "16-bit",
            "codec": "PCM",
            "bitrate_mono": "256 kbps",
            "bitrate_stereo": "512 kbps"
        }
    }

@app.delete("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up stored data for a session."""
    import os
    import glob
    
    if session_id in generated_calls_storage:
        del generated_calls_storage[session_id]
    
    audio_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_audio')
    audio_files = glob.glob(os.path.join(audio_dir, f"{session_id}_*.wav"))
    for file_path in audio_files:
        try:
            os.remove(file_path)
        except OSError:
            pass  # File already deleted or doesn't exist
    
    transcript_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_transcripts')
    transcript_files = glob.glob(os.path.join(transcript_dir, f"contoso_call_*_call_*.txt"))
    for file_path in transcript_files:
        try:
            os.remove(file_path)
        except OSError:
            pass  # File already deleted or doesn't exist
    
    return {"message": f"Session {session_id} cleaned up successfully"}

@app.get("/stats")
async def get_stats():
    """Get API usage statistics."""
    import os
    import glob
    
    total_sessions = len(generated_calls_storage)
    total_calls = sum(len(calls) for calls in generated_calls_storage.values())
    
    audio_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_audio')
    audio_files = glob.glob(os.path.join(audio_dir, "*.wav")) if os.path.exists(audio_dir) else []
    total_audio_files = len(audio_files)
    
    transcript_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_transcripts')
    transcript_files = glob.glob(os.path.join(transcript_dir, "*.txt")) if os.path.exists(transcript_dir) else []
    total_transcript_files = len(transcript_files)
    
    return {
        "total_sessions": total_sessions,
        "total_calls_generated": total_calls,
        "total_audio_files": total_audio_files,
        "total_transcript_files": total_transcript_files,
        "audio_directory": audio_dir,
        "transcript_directory": transcript_dir
    }
