from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ScenarioType(str, Enum):
    HEALTHCARE_PROVIDER = "healthcare_provider"
    PATIENT_VISIT = "patient_visit"
    CAREGIVER_INQUIRY = "caregiver_inquiry"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"

class DurationType(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class AudioSettings(BaseModel):
    sampling_rate: int = 16000  # 8000, 16000, 32000, 48000
    channels: int = 1  # 1 for mono, 2 for stereo
    generate_audio: bool = True
    save_audio_locally: bool = True

class CallGenerationRequest(BaseModel):
    scenarios: List[ScenarioType]
    sentiment: SentimentType = SentimentType.MIXED
    duration: DurationType = DurationType.MEDIUM
    num_calls: int = 5
    audio_settings: AudioSettings = AudioSettings()
    save_transcripts_locally: bool = True

class TranscriptData(BaseModel):
    transcript: str
    scenario: str
    sentiment: str
    duration: str
    participants: List[str]
    synthetic_data: Dict[str, Any]
    metadata: Dict[str, Any]

class GeneratedCall(BaseModel):
    id: int
    scenario: str
    transcript_data: TranscriptData
    audio_file_url: Optional[str] = None
    transcript_file_url: Optional[str] = None

class CallGenerationResponse(BaseModel):
    calls: List[GeneratedCall]
    total_calls: int
    generation_time: float
