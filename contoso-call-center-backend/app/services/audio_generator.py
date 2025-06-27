import io
import wave
import numpy as np
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pydub.generators import Sine
import tempfile
import os
from typing import Dict, Optional, Tuple, Union
import base64
import gender_guesser.detector as gender

class AudioGenerator:
    def __init__(self):
        self.voice_settings = {
            'agent': {
                'male': {'voice_name': 'en-US-BrianNeural'},    # US English, professional male voice
                'female': {'voice_name': 'en-US-JennyNeural'}   # US English, professional female voice
            },
            'caller': {
                'male': {'voice_name': 'en-GB-RyanNeural'},     # UK English, professional male voice
                'female': {'voice_name': 'en-GB-SoniaNeural'}   # UK English, professional female voice
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

    def generate_audio(self, transcript: str, audio_settings: Dict, audio_id: Optional[str] = None, save_locally: bool = True) -> Optional[Union[str, bytes]]:
        """Generate audio file from transcript. Returns file path if saving locally and audio_id provided, otherwise bytes."""
        try:
            segments = self._parse_transcript(transcript)

            audio_segments = []

            for i, (speaker, text) in enumerate(segments):
                speaker_name = self._extract_name_from_speaker(speaker, transcript)
                voice_config = self._get_voice_config(speaker, speaker_name)


                segment_audio = self._text_to_speech(text, voice_config)

                if segment_audio:
                    segment_audio = self._apply_voice_characteristics(segment_audio, speaker)
                    audio_segments.append(segment_audio)

                    if i < len(segments) - 1:
                        pause = AudioSegment.silent(duration=500)  # 0.5 second pause
                        audio_segments.append(pause)

            if not audio_segments:
                return None

            print(f"Debug: About to combine {len(audio_segments)} audio segments")
            for i, segment in enumerate(audio_segments):
                print(f"Debug: Segment {i}: type={type(segment)}, length={len(segment)}ms, channels={segment.channels}")

            combined_audio = self._combine_audio_segments(audio_segments)

            final_audio = self._apply_audio_settings(combined_audio, audio_settings)
            print(f"Debug: Audio settings applied - Final length: {len(final_audio)}ms")

            if audio_id and save_locally:
                result = self._save_to_file(final_audio, audio_settings, audio_id)
                print(f"Debug: File saved to: {result}")
                return result
            else:
                return self._to_wav_bytes(final_audio, audio_settings)

        except Exception as e:
            print(f"Error generating audio: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return None

    def _parse_transcript(self, transcript: str) -> list:
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
                    if text:  # Only add non-empty text
                        segments.append((speaker, text))

        return segments

    def _get_voice_config(self, speaker: str, speaker_name: Optional[str] = None) -> Dict:
        """Get voice configuration based on speaker type and name gender."""
        speaker_type = 'agent' if 'agent' in speaker.lower() else 'caller'

        if speaker_name:
            gender = self._detect_gender_from_name(speaker_name)
            return self.voice_settings[speaker_type][gender]
        else:
            return self.voice_settings[speaker_type]['female']

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
                return ' '.join(parts[1:])  # Return everything after "Agent"
            else:
                return speaker  # Fallback to full speaker label
        else:
            name = speaker.replace('Dr.', '').replace('Mr.', '').replace('Ms.', '').replace('Mrs.', '').strip()
            return name if name else speaker

    def _apply_voice_characteristics(self, audio: AudioSegment, speaker: str) -> AudioSegment:
        """Apply voice characteristics to differentiate speakers."""
        if 'agent' in speaker.lower():
            audio = audio + 2  # Slightly increase volume
            audio = audio.speedup(playback_speed=1.05)  # Slightly faster, professional pace
        else:
            audio = audio - 1  # Slightly decrease volume

        return audio

    def _text_to_speech(self, text: str, voice_config: Dict) -> Optional[AudioSegment]:
        """Convert text to speech using Azure Speech SDK."""
        import time
        import gc
        import tempfile
        temp_filename = None
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=os.environ.get('SPEECH_KEY'),
                region="westus3"
            )
            speech_config.speech_synthesis_voice_name = voice_config['voice_name']

            temp_dir = tempfile.gettempdir()
            
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            temp_filename = os.path.join(temp_dir, f"azure_tts_{unique_id}.wav")
            
            temp_filename = os.path.abspath(temp_filename)
            temp_filename = os.path.normpath(temp_filename)
            
            normalized_path = temp_filename.replace('\\', '/')
            print(f"Debug: Azure SDK will create file at: {normalized_path}")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=normalized_path)
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

            # Wait for file to be written
            for _ in range(20):
                if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                    break
                time.sleep(0.05)

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if os.path.exists(temp_filename):
                    with open(temp_filename, 'rb') as f:
                        audio = AudioSegment.from_file(f, format='wav')
                    gc.collect()
                    # Retry deletion up to 10 times
                    for _ in range(10):
                        try:
                            os.unlink(temp_filename)
                            break
                        except (OSError, PermissionError):
                            time.sleep(0.1)
                    return audio
                else:
                    print(f"TTS succeeded but file not found: {temp_filename}")
                    return None
            else:
                print(f"Speech synthesis failed: {speech_synthesis_result.reason}")
                if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_synthesis_result.cancellation_details
                    print(f"Error details: {cancellation_details.error_details}")
                if temp_filename and os.path.exists(temp_filename):
                    for _ in range(10):
                        try:
                            os.unlink(temp_filename)
                            break
                        except (OSError, PermissionError):
                            time.sleep(0.1)
                return None

        except Exception as e:
            print(f"Error in Azure text-to-speech: {e}")
            if temp_filename and os.path.exists(temp_filename):
                for _ in range(10):
                    try:
                        os.unlink(temp_filename)
                        break
                    except (OSError, PermissionError):
                        time.sleep(0.1)
            return None

    def _apply_audio_settings(self, audio: AudioSegment, settings: Dict) -> AudioSegment:
        """Apply audio settings to the combined audio."""

        target_sample_rate = settings.get('sampling_rate', 16000)
        audio = audio.set_frame_rate(target_sample_rate)

        target_channels = settings.get('channels', 1)
        if target_channels == 1:
            audio = audio.set_channels(1)  # Convert to mono
        else:
            audio = audio.set_channels(2)  # Convert to stereo

        audio = audio.normalize()

        return audio

    def _to_wav_bytes(self, audio: AudioSegment, settings: Dict) -> bytes:
        """Convert AudioSegment to WAV bytes with Windows-compatible fallback."""

        wav_buffer = io.BytesIO()

        try:
            print("Debug: Attempting direct WAV export to bytes (no ffmpeg dependency)...")
            audio.export(wav_buffer, format="wav")
            print("Debug: Direct WAV export to bytes successful")
        except Exception as direct_error:
            print(f"Debug: Direct WAV export to bytes failed: {direct_error}")
            print("Debug: Trying WAV export to bytes with explicit parameters (requires ffmpeg)...")
            
            wav_buffer = io.BytesIO()  # Reset buffer
            audio.export(
                wav_buffer,
                format="wav",
                parameters=[
                    "-acodec", "pcm_s16le",  # 16-bit PCM
                    "-ar", str(settings.get('sampling_rate', 16000)),  # Sample rate
                    "-ac", str(settings.get('channels', 1))  # Channels
                ]
            )
            print("Debug: Parametric WAV export to bytes successful")

        wav_buffer.seek(0)
        return wav_buffer.getvalue()

    def _save_to_file(self, audio: AudioSegment, settings: Dict, audio_id: str) -> str:
        """Save AudioSegment to WAV file and return file path."""
        import os

        print(f"Debug: Saving audio - Length: {len(audio)}ms, Channels: {audio.channels}, Frame rate: {audio.frame_rate}")

        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_audio')
        os.makedirs(audio_dir, exist_ok=True)

        file_path = os.path.join(audio_dir, f"{audio_id}.wav")
        print(f"Debug: Saving to file path: {file_path}")

        try:
            try:
                print("Debug: Attempting direct WAV export (no ffmpeg dependency)...")
                audio.export(file_path, format="wav")
                print("Debug: Direct WAV export successful")
            except Exception as direct_error:
                print(f"Debug: Direct WAV export failed: {direct_error}")
                print("Debug: Trying WAV export with explicit parameters (requires ffmpeg)...")
                
                audio.export(
                    file_path,
                    format="wav",
                    parameters=[
                        "-acodec", "pcm_s16le",  # 16-bit PCM
                        "-ar", str(settings.get('sampling_rate', 16000)),  # Sample rate
                        "-ac", str(settings.get('channels', 1))  # Channels
                    ]
                )
                print("Debug: Parametric WAV export successful")
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"Debug: File created successfully - Size: {file_size} bytes")
                if file_size == 0:
                    print("Debug: WARNING - File has 0 bytes!")
                return file_path
            else:
                raise FileNotFoundError(f"File was not created: {file_path}")
                
        except Exception as e:
            print(f"Debug: Error during audio export: {e}")
            import traceback
            print(f"Full export traceback: {traceback.format_exc()}")
            raise

        return file_path

    def _combine_audio_segments(self, audio_segments: list) -> AudioSegment:
        """Combine audio segments with Windows-compatible fallback method."""
        if not audio_segments:
            raise ValueError("No audio segments to combine")
        
        if len(audio_segments) == 1:
            return audio_segments[0]
        
        print(f"Debug: Combining {len(audio_segments)} audio segments")
        
        try:
            combined_audio = sum(audio_segments)
            print("Debug: sum() method successful")
            return combined_audio
        except Exception as e:
            print(f"Debug: sum() method failed: {e}, trying alternative...")
            
            try:
                combined_audio = audio_segments[0]
                for i, segment in enumerate(audio_segments[1:], 1):
                    print(f"Debug: Adding segment {i}")
                    combined_audio = combined_audio + segment
                print("Debug: Manual combination successful")
                return combined_audio
            except Exception as e2:
                print(f"Debug: Manual combination also failed: {e2}")
                raise Exception(f"Both combination methods failed: sum() error: {e}, manual error: {e2}")

    def _safe_delete_temp_file(self, temp_filename: str) -> None:
        """Safely delete temporary file with retry logic for Windows file locking."""
        import time
        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                break
            except (OSError, PermissionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Warning: Could not delete temporary file {temp_filename}: {e}")

    def simulate_phone_quality(self, audio: AudioSegment) -> AudioSegment:
        """Apply phone-like audio filtering."""


        audio = audio.low_pass_filter(3400)

        audio = audio.high_pass_filter(300)

        audio = audio.compress_dynamic_range()

        return audio
