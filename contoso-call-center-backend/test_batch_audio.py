#!/usr/bin/env python3
"""
Test script for Azure Batch Audio Generator
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

from app.services.azure_batch_audio_generator import AzureBatchAudioGenerator

def test_batch_audio_generator():
    """Test the batch audio generator with a simple transcript."""
    
    if not os.environ.get('SPEECH_KEY'):
        print("Error: SPEECH_KEY environment variable not set")
        return False
    
    sample_transcript = """Agent Sarah: Thank you for calling Contoso Medical, this is Sarah. How can I help you today?
Dr. Smith: Hi Sarah, this is Dr. Smith from General Hospital. I'm calling about a patient encounter from last week.
Agent Sarah: Of course, Dr. Smith. I'd be happy to help you with that. Can you provide me with the patient's information?
Dr. Smith: Yes, the patient's name is John Doe, date of birth March 15, 1980."""
    
    audio_settings = {
        'sampling_rate': 16000,
        'channels': 1
    }
    
    try:
        print("Initializing Azure Batch Audio Generator...")
        generator = AzureBatchAudioGenerator()
        
        print("Testing SSML generation...")
        ssml = generator._create_ssml_document(sample_transcript)
        print(f"Generated SSML length: {len(ssml)} characters")
        print("SSML preview:")
        print(ssml[:500] + "..." if len(ssml) > 500 else ssml)
        
        print("\nTesting transcript parsing...")
        segments = generator._parse_transcript(sample_transcript)
        print(f"Parsed {len(segments)} segments:")
        for i, (speaker, text) in enumerate(segments):
            print(f"  {i+1}. {speaker}: {text[:50]}...")
        
        print("\nBatch audio generator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing batch audio generator: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("Testing Azure Batch Audio Generator...")
    success = test_batch_audio_generator()
    sys.exit(0 if success else 1)
