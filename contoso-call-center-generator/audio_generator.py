import io
import wave
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import tempfile
import os
from typing import Dict, Optional

class AudioGenerator:
    def __init__(self):
        self.voice_settings = {
            'agent': {'lang': 'en', 'tld': 'com', 'slow': False},
            'caller': {'lang': 'en', 'tld': 'ca', 'slow': False}  # Different accent for variety
        }
    
    def generate_audio(self, transcript: str, audio_settings: Dict) -> Optional[bytes]:
        """Generate audio file from transcript."""
        try:
            segments = self._parse_transcript(transcript)
            
            audio_segments = []
            
            for i, (speaker, text) in enumerate(segments):
                voice_config = self._get_voice_config(speaker)
                
                segment_audio = self._text_to_speech(text, voice_config)
                
                if segment_audio:
                    audio_segments.append(segment_audio)
                    
                    if i < len(segments) - 1:
                        pause = AudioSegment.silent(duration=500)  # 0.5 second pause
                        audio_segments.append(pause)
            
            if not audio_segments:
                return None
            
            combined_audio = sum(audio_segments)
            
            final_audio = self._apply_audio_settings(combined_audio, audio_settings)
            
            return self._to_wav_bytes(final_audio, audio_settings)
            
        except Exception as e:
            print(f"Error generating audio: {e}")
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
    
    def _get_voice_config(self, speaker: str) -> Dict:
        """Get voice configuration based on speaker."""
        if 'agent' in speaker.lower():
            return self.voice_settings['agent']
        else:
            return self.voice_settings['caller']
    
    def _text_to_speech(self, text: str, voice_config: Dict) -> Optional[AudioSegment]:
        """Convert text to speech using gTTS."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_filename = temp_file.name
            
            tts = gTTS(
                text=text,
                lang=voice_config['lang'],
                tld=voice_config['tld'],
                slow=voice_config['slow']
            )
            
            tts.save(temp_filename)
            
            audio = AudioSegment.from_mp3(temp_filename)
            
            os.unlink(temp_filename)
            
            return audio
            
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
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
        """Convert AudioSegment to WAV bytes."""
        
        wav_buffer = io.BytesIO()
        
        audio.export(
            wav_buffer,
            format="wav",
            parameters=[
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", str(settings.get('sampling_rate', 16000)),  # Sample rate
                "-ac", str(settings.get('channels', 1))  # Channels
            ]
        )
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()
    
    def add_background_noise(self, audio: AudioSegment, noise_level: float = 0.1) -> AudioSegment:
        """Add subtle background noise to make audio more realistic."""
        
        noise_duration = len(audio)
        noise = AudioSegment.silent(duration=noise_duration)
        
        for freq in [50, 120, 200]:  # Low frequency background noise
            sine_wave = Sine(freq).to_audio_segment(duration=noise_duration)
            sine_wave = sine_wave - 40  # Make it very quiet
            noise = noise.overlay(sine_wave)
        
        return audio.overlay(noise, gain_during_overlay=-20)
    
    def simulate_phone_quality(self, audio: AudioSegment) -> AudioSegment:
        """Apply phone-like audio filtering."""
        
        
        audio = audio.low_pass_filter(3400)
        
        audio = audio.high_pass_filter(300)
        
        audio = audio.compress_dynamic_range()
        
        return audio
