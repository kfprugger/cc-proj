import streamlit as st
import os
import json
import wave
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import zipfile
import io

from transcript_generator import TranscriptGenerator
from audio_generator import AudioGenerator
from data_generator import SyntheticDataGenerator

def main():
    st.set_page_config(
        page_title="Contoso Call Center Synthetic Transcript and Audio Generator",
        page_icon="📞",
        layout="wide"
    )
    
    st.title("📞 Contoso Call Center Synthetic Transcript and Audio Generator")
    st.markdown("---")
    
    st.warning("""
    **DISCLAIMER**: All generated data is synthetic and fictitious. 
    This application is for simulation purposes only and does not contain real PHI or PII data.
    """)
    
    if 'transcript_gen' not in st.session_state:
        st.session_state.transcript_gen = TranscriptGenerator()
    if 'audio_gen' not in st.session_state:
        st.session_state.audio_gen = AudioGenerator()
    if 'data_gen' not in st.session_state:
        st.session_state.data_gen = SyntheticDataGenerator()
    
    st.header("🔧 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scenario Selection")
        scenarios = {
            "healthcare_provider": "Healthcare provider inquiring about a past patient encounter",
            "patient_visit": "Patient calling about a recent visit to a hospital, clinic, or emergency room",
            "caregiver_inquiry": "Caregiver calling with a medical question about a patient under Contoso Medical's care"
        }
        
        selected_scenarios = []
        for key, description in scenarios.items():
            if st.checkbox(description, key=key):
                selected_scenarios.append(key)
        
        st.subheader("Call Parameters")
        sentiment_mix = st.selectbox(
            "Sentiment Mix",
            ["Positive", "Neutral", "Negative", "Mixed (Random)"],
            index=3
        )
        
        call_duration = st.selectbox(
            "Call Duration",
            ["Short (1-3 minutes)", "Medium (3-7 minutes)", "Long (7-15 minutes)"],
            index=1
        )
        
        num_calls = st.number_input(
            "Number of calls to generate",
            min_value=1,
            max_value=50,
            value=5
        )
    
    with col2:
        st.subheader("Audio Generation")
        generate_audio = st.checkbox("Generate Audio Files (.wav)", value=True)
        
        if generate_audio:
            st.subheader("Audio Settings")
            sampling_rate = st.selectbox(
                "Sampling Rate",
                ["8 kHz", "16 kHz", "32 kHz", "48 kHz"],
                index=1
            )
            
            channels = st.selectbox(
                "Channels",
                ["Mono (Recommended)", "Stereo"],
                index=0
            )
            
            st.info(f"""
            **Audio Specifications:**
            - Format: WAV (Microsoft PCM)
            - Bit Depth: 16-bit
            - Sampling Rate: {sampling_rate}
            - Channels: {channels.split(' ')[0]}
            - Bitrate: {'256 kbps' if 'Mono' in channels else '512 kbps'}
            - Codec: PCM
            """)
    
    st.markdown("---")
    
    if st.button("🚀 Generate Calls", type="primary", use_container_width=True):
        if not selected_scenarios:
            st.error("Please select at least one scenario.")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        generated_calls = []
        
        for i in range(num_calls):
            status_text.text(f"Generating call {i+1} of {num_calls}...")
            
            import random
            scenario = random.choice(selected_scenarios)
            
            transcript_data = st.session_state.transcript_gen.generate_transcript(
                scenario=scenario,
                sentiment=sentiment_mix,
                duration=call_duration
            )
            
            audio_file = None
            if generate_audio:
                audio_settings = {
                    'sampling_rate': int(sampling_rate.split()[0]) * 1000,
                    'channels': 1 if 'Mono' in channels else 2
                }
                audio_file = st.session_state.audio_gen.generate_audio(
                    transcript_data['transcript'],
                    audio_settings
                )
            
            generated_calls.append({
                'id': i + 1,
                'scenario': scenario,
                'transcript_data': transcript_data,
                'audio_file': audio_file
            })
            
            progress_bar.progress((i + 1) / num_calls)
        
        status_text.text("Generation complete!")
        st.session_state.generated_calls = generated_calls
        st.success(f"Successfully generated {num_calls} calls!")
    
    if 'generated_calls' in st.session_state and st.session_state.generated_calls:
        st.markdown("---")
        st.header("📋 Generated Calls")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Calls", len(st.session_state.generated_calls))
        with col2:
            scenarios_count = {}
            for call in st.session_state.generated_calls:
                scenario = call['scenario']
                scenarios_count[scenario] = scenarios_count.get(scenario, 0) + 1
            st.metric("Scenarios Used", len(scenarios_count))
        with col3:
            audio_count = sum(1 for call in st.session_state.generated_calls if call['audio_file'])
            st.metric("Audio Files", audio_count)
        
        for call in st.session_state.generated_calls:
            with st.expander(f"Call #{call['id']} - {scenarios[call['scenario']]}"):
                transcript_data = call['transcript_data']
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Transcript")
                    st.text_area(
                        "Full Transcript",
                        transcript_data['transcript'],
                        height=300,
                        key=f"transcript_{call['id']}"
                    )
                
                with col2:
                    st.subheader("Call Details")
                    st.json({
                        "Scenario": call['scenario'],
                        "Duration": transcript_data.get('duration', 'N/A'),
                        "Sentiment": transcript_data.get('sentiment', 'N/A'),
                        "Participants": transcript_data.get('participants', []),
                        "Generated PHI/PII": transcript_data.get('synthetic_data', {})
                    })
                    
                    if call['audio_file']:
                        st.subheader("Audio")
                        st.audio(call['audio_file'], format='audio/wav')
        
        st.markdown("---")
        st.header("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download All Transcripts", use_container_width=True):
                zip_buffer = create_transcript_zip(st.session_state.generated_calls)
                st.download_button(
                    label="Download Transcripts ZIP",
                    data=zip_buffer,
                    file_name=f"contoso_transcripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
        
        with col2:
            if generate_audio and any(call['audio_file'] for call in st.session_state.generated_calls):
                if st.button("🎵 Download All Audio Files", use_container_width=True):
                    zip_buffer = create_audio_zip(st.session_state.generated_calls)
                    st.download_button(
                        label="Download Audio ZIP",
                        data=zip_buffer,
                        file_name=f"contoso_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )

def create_transcript_zip(calls: List[Dict]) -> bytes:
    """Create a ZIP file containing all transcripts."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for call in calls:
            filename = f"call_{call['id']:03d}_transcript.txt"
            transcript_content = f"""Contoso Medical Call Center - Call #{call['id']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Scenario: {call['scenario']}

{call['transcript_data']['transcript']}

---
Call Metadata:
{json.dumps(call['transcript_data'].get('metadata', {}), indent=2)}
"""
            zip_file.writestr(filename, transcript_content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_audio_zip(calls: List[Dict]) -> bytes:
    """Create a ZIP file containing all audio files."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for call in calls:
            if call['audio_file']:
                filename = f"call_{call['id']:03d}_audio.wav"
                zip_file.writestr(filename, call['audio_file'])
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if __name__ == "__main__":
    main()
