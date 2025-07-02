import json
import time
import requests
import os
from typing import Dict, List, Optional, Tuple, Union
import uuid
from datetime import datetime
import gender_guesser.detector as gender


class AzureBatchAudioGenerator:
    def __init__(self):
        self.speech_key = os.environ.get('SPEECH_KEY')
        self.speech_region = os.environ.get('SPEECH_REGION', 'westus3')
        self.base_url = f"https://{self.speech_region}.customvoice.api.speech.microsoft.com"
        
        self.voice_settings = {
            'agent': {
                'male': {'voice_name': 'en-US-BrianNeural'},
                'female': {'voice_name': 'en-US-JennyNeural'}
            },
            'caller': {
                'male': {'voice_name': 'en-GB-RyanNeural'},
                'female': {'voice_name': 'en-GB-SoniaNeural'}
            }
        }

    def _detect_gender_from_name(self, name: str) -> str:
        """Detect gender from a given name. Returns 'male' or 'female'."""
        d = gender.Detector()
        first_name = name.split()[0] if ' ' in name else name
        first_name = first_name.replace('Dr.', '').replace('Mr.', '').replace('Ms.', '').replace('Mrs.', '').strip()
        
        gender_result = d.get_gender(first_name)
        
        if gender_result in ['male', 'mostly_male']:
            return 'male'
        elif gender_result in ['female', 'mostly_female']:
            return 'female'
        else:
            return 'female'

    def _extract_name_from_speaker(self, speaker: str, transcript_text: Optional[str] = None) -> str:
        """Extract the actual name from speaker label or transcript context."""
        if 'Agent' in speaker and transcript_text:
            import re
            agent_intro_pattern = r'this is (\w+)'
            match = re.search(agent_intro_pattern, transcript_text, re.IGNORECASE)
            if match:
                return match.group(1)

        if 'Agent' in speaker:
            parts = speaker.split()
            if len(parts) > 1:
                return ' '.join(parts[1:])
            else:
                return speaker
        else:
            name = speaker.replace('Dr.', '').replace('Mr.', '').replace('Ms.', '').replace('Mrs.', '').strip()
            return name if name else speaker

    def _get_voice_config(self, speaker: str, speaker_name: Optional[str] = None) -> Dict:
        """Get voice configuration based on speaker type and name gender."""
        speaker_type = 'agent' if 'agent' in speaker.lower() else 'caller'
        
        if speaker_name:
            gender = self._detect_gender_from_name(speaker_name)
            return self.voice_settings[speaker_type][gender]
        else:
            return self.voice_settings[speaker_type]['female']

    def _parse_transcript(self, transcript: str) -> List[Tuple[str, str]]:
        """Parse transcript into speaker segments."""
        segments = []
        lines = transcript.split('\n')

        for line in lines:
            line = line.strip()
            if ':' in line and line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    text = parts[1].strip()
                    if text:
                        segments.append((speaker, text))

        return segments

    def _create_ssml_document(self, transcript: str) -> str:
        """Create SSML document from transcript with multiple speakers and pauses."""
        segments = self._parse_transcript(transcript)
        
        ssml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        ssml_parts.append('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">')
        
        for i, (speaker, text) in enumerate(segments):
            speaker_name = self._extract_name_from_speaker(speaker, transcript)
            voice_config = self._get_voice_config(speaker, speaker_name)
            voice_name = voice_config['voice_name']
            
            if 'agent' in speaker.lower():
                rate = "1.05"
                volume = "+2dB"
            else:
                rate = "1.0"
                volume = "-1dB"
            
            ssml_parts.append(f'<voice name="{voice_name}">')
            ssml_parts.append(f'<prosody rate="{rate}" volume="{volume}">')
            ssml_parts.append(text)
            ssml_parts.append('</prosody>')
            ssml_parts.append('</voice>')
            
            if i < len(segments) - 1:
                ssml_parts.append('<break time="500ms"/>')
        
        ssml_parts.append('</speak>')
        return ''.join(ssml_parts)

    def _submit_batch_job(self, ssml_content: str, audio_settings: Dict, job_name: str) -> str:
        """Submit batch synthesis job to Azure Speech API."""
        url = f"{self.base_url}/api/texttospeech/3.1-preview1/batchsynthesis"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.speech_key,
            'Content-Type': 'application/json'
        }
        
        output_format = self._get_output_format(audio_settings)
        
        payload = {
            "displayName": job_name,
            "description": f"Batch synthesis job for {job_name}",
            "textType": "SSML",
            "inputs": [
                {
                    "text": ssml_content
                }
            ],
            "properties": {
                "outputFormat": output_format,
                "concatenateResult": True,
                "destinationContainerUrl": None
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            job_data = response.json()
            return job_data['id']
        else:
            raise Exception(f"Failed to submit batch job: {response.status_code} - {response.text}")

    def _get_output_format(self, audio_settings: Dict) -> str:
        """Convert audio settings to Azure output format string."""
        sample_rate = audio_settings.get('sampling_rate', 16000)
        channels = audio_settings.get('channels', 1)
        
        format_map = {
            (8000, 1): "riff-8khz-16bit-mono-pcm",
            (16000, 1): "riff-16khz-16bit-mono-pcm",
            (32000, 1): "riff-32khz-16bit-mono-pcm",
            (48000, 1): "riff-48khz-16bit-mono-pcm",
            (16000, 2): "riff-16khz-16bit-stereo-pcm",
            (48000, 2): "riff-48khz-16bit-stereo-pcm"
        }
        
        return format_map.get((sample_rate, channels), "riff-16khz-16bit-mono-pcm")

    def _poll_job_status(self, job_id: str, timeout: int = 300) -> Dict:
        """Poll job status until completion or timeout."""
        url = f"{self.base_url}/api/texttospeech/3.1-preview1/batchsynthesis/{job_id}"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.speech_key
        }
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                job_data = response.json()
                status = job_data.get('status')
                
                print(f"Debug: Batch job {job_id} status: {status}")
                
                if status == 'Succeeded':
                    return job_data
                elif status == 'Failed':
                    raise Exception(f"Batch synthesis job failed: {job_data.get('properties', {}).get('error', 'Unknown error')}")
                elif status in ['NotStarted', 'Running']:
                    time.sleep(5)  # Wait 5 seconds before next poll
                    continue
                else:
                    raise Exception(f"Unknown job status: {status}")
            else:
                raise Exception(f"Failed to get job status: {response.status_code} - {response.text}")
        
        raise Exception(f"Job {job_id} timed out after {timeout} seconds")

    def _download_audio_result(self, job_data: Dict) -> bytes:
        """Download the synthesized audio from the job results."""
        outputs = job_data.get('outputs', {})
        result_url = outputs.get('result')
        
        if not result_url:
            raise Exception("No result URL found in job data")
        
        print(f"Debug: Downloading audio from: {result_url}")
        
        response = requests.get(result_url)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download audio: {response.status_code} - {response.text}")

    def generate_audio(self, transcript: str, audio_settings: Dict, audio_id: Optional[str] = None, save_locally: bool = True) -> Optional[Union[str, bytes]]:
        """Generate audio using Azure Batch Synthesis API."""
        try:
            print(f"Debug: Starting batch synthesis for audio_id: {audio_id}")
            
            ssml_content = self._create_ssml_document(transcript)
            print(f"Debug: Generated SSML length: {len(ssml_content)} characters")
            
            job_name = audio_id or f"batch_job_{int(time.time())}"
            job_id = self._submit_batch_job(ssml_content, audio_settings, job_name)
            print(f"Debug: Submitted batch job with ID: {job_id}")
            
            job_data = self._poll_job_status(job_id)
            print(f"Debug: Job completed successfully")
            
            audio_bytes = self._download_audio_result(job_data)
            print(f"Debug: Downloaded audio, size: {len(audio_bytes)} bytes")
            
            if audio_id and save_locally:
                return self._save_audio_to_file(audio_bytes, audio_id)
            else:
                return audio_bytes
                
        except Exception as e:
            print(f"Error in batch audio generation: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return None

    def _save_audio_to_file(self, audio_bytes: bytes, audio_id: str) -> str:
        """Save audio bytes to file and return file path."""
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        file_path = os.path.join(audio_dir, f"{audio_id}.wav")
        
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"Debug: Saved audio to: {file_path}")
        return file_path
