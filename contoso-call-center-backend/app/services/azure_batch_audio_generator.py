import json
import time
import requests
import os
from typing import Dict, List, Optional, Tuple, Union
import uuid
from datetime import datetime
import gender_guesser.detector as gender
import zipfile
import io
from pydub import AudioSegment


class AzureBatchAudioGenerator:
    def __init__(self):
        self.speech_key = os.environ.get('SPEECH_KEY')
        self.speech_region = os.environ.get('SPEECH_REGION', 'westus3')
        
        custom_endpoint = os.environ.get('ENDPOINT')
        if custom_endpoint:
            self.base_url = custom_endpoint.rstrip('/')
        else:
            self.base_url = f"https://{self.speech_region}.api.cognitive.microsoft.com"
        
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
        
        ssml_parts = ['<speak version="1.0" xml:lang="en-US">']
        
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
        synthesis_id = f"batch_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        url = f"{self.base_url}/texttospeech/batchsyntheses/{synthesis_id}?api-version=2024-04-01"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.speech_key,
            'Content-Type': 'application/json'
        }
        
        output_format = self._get_output_format(audio_settings)
        
        payload = {
            "description": f"Batch synthesis job for {job_name}",
            "inputKind": "SSML",
            "inputs": [
                {
                    "content": ssml_content
                }
            ],
            "properties": {
                "outputFormat": output_format,
                "concatenateResult": audio_settings.get('concatenate_result', False),
                "wordBoundaryEnabled": False,
                "sentenceBoundaryEnabled": False,
                "decompressOutputFiles": False
            }
        }
        
        print(f"Debug: Speech key length: {len(self.speech_key) if self.speech_key else 'None'}")
        print(f"Debug: Speech region: {self.speech_region}")
        print(f"Debug: Submitting to URL: {url}")
        print(f"Debug: Headers: {headers}")
        print(f"Debug: SSML content length: {len(ssml_content)}")
        print(f"Debug: Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.put(url, headers=headers, json=payload)
        
        print(f"Debug: Response status: {response.status_code}")
        print(f"Debug: Response headers: {dict(response.headers)}")
        print(f"Debug: Response text: {response.text}")
        
        if response.status_code == 201:
            job_data = response.json()
            return synthesis_id
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
        url = f"{self.base_url}/texttospeech/batchsyntheses/{job_id}?api-version=2024-04-01"
        
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

    def _download_audio_result(self, job_data: Dict, concatenate_result: bool = False) -> bytes:
        """Download the synthesized audio from the job results."""
        outputs = job_data.get('outputs', {})
        result_url = outputs.get('result')
        
        if not result_url:
            raise Exception("No result URL found in job data")
        
        print(f"Debug: Downloading audio from: {result_url}")
        
        response = requests.get(result_url)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if concatenate_result:
                return response.content
            elif 'application/zip' in content_type or result_url.endswith('.zip'):
                return self._handle_zip_audio_result(response.content)
            else:
                return response.content
        else:
            raise Exception(f"Failed to download audio: {response.status_code} - {response.text}")

    def _extract_and_concatenate_zip(self, zip_content: bytes) -> bytes:
        """Extract audio files from ZIP and concatenate them locally."""
        try:
            import wave
            
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
                audio_files = [f for f in zip_file.namelist() if f.endswith('.wav')]
                audio_files.sort()  # Ensure consistent order
                
                if not audio_files:
                    raise Exception("No audio files found in ZIP archive")
                
                print(f"Debug: Found {len(audio_files)} audio files in ZIP: {audio_files}")
                
                first_file_data = zip_file.read(audio_files[0])
                first_wave = wave.open(io.BytesIO(first_file_data), 'rb')
                params = first_wave.getparams()
                first_wave.close()
                
                output_buffer = io.BytesIO()
                output_wave = wave.open(output_buffer, 'wb')
                output_wave.setparams(params)
                
                for audio_file in audio_files:
                    file_data = zip_file.read(audio_file)
                    file_wave = wave.open(io.BytesIO(file_data), 'rb')
                    output_wave.writeframes(file_wave.readframes(file_wave.getnframes()))
                    file_wave.close()
                
                output_wave.close()
                concatenated_audio = output_buffer.getvalue()
                output_buffer.close()
                
                print(f"Debug: Concatenated {len(audio_files)} files into {len(concatenated_audio)} bytes")
                return concatenated_audio
                
        except Exception as e:
            print(f"Error extracting and concatenating ZIP: {e}")
            return zip_content

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
            
            concatenate_result = audio_settings.get('concatenate_result', False)
            audio_bytes = self._download_audio_result(job_data, concatenate_result)
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

    def _handle_zip_audio_result(self, zip_content: bytes) -> bytes:
        """Handle ZIP archive containing multiple audio files and concatenate them."""
        print("Debug: Processing ZIP archive with multiple audio files")
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
                audio_files = [f for f in zip_file.namelist() if f.endswith('.wav')]
                audio_files.sort()  # Ensure consistent ordering
                
                if not audio_files:
                    raise Exception("No audio files found in ZIP archive")
                
                print(f"Debug: Found {len(audio_files)} audio files in ZIP: {audio_files}")
                
                combined_audio = None
                
                for audio_file in audio_files:
                    with zip_file.open(audio_file) as f:
                        audio_data = f.read()
                        audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
                        
                        if combined_audio is None:
                            combined_audio = audio_segment
                        else:
                            # Add a small pause between segments
                            pause = AudioSegment.silent(duration=500)  # 500ms pause
                            combined_audio = combined_audio + pause + audio_segment
                
                output_buffer = io.BytesIO()
                combined_audio.export(output_buffer, format="wav")
                
                print(f"Debug: Successfully concatenated {len(audio_files)} audio files")
                return output_buffer.getvalue()
                
        except Exception as e:
            print(f"Error processing ZIP audio result: {e}")
            raise Exception(f"Failed to process ZIP audio result: {e}")

    def _save_audio_to_file(self, audio_bytes: bytes, audio_id: str) -> str:
        """Save audio bytes to file and return file path."""
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        file_path = os.path.join(audio_dir, f"{audio_id}.wav")
        
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"Debug: Saved audio to: {file_path}")
        return file_path
