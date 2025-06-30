import os
import json
from typing import Dict, List, Any
from datetime import datetime
from openai import AzureOpenAI
from .data_generator import SyntheticDataGenerator

class AzureOpenAITranscriptGenerator:
    def __init__(self):
        self.data_gen = SyntheticDataGenerator()
        
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        self.scenario_prompts = {
            'healthcare_provider': self._get_healthcare_provider_prompt,
            'patient_visit': self._get_patient_visit_prompt,
            'caregiver_inquiry': self._get_caregiver_inquiry_prompt
        }
    
    def generate_transcript(self, scenario: str, sentiment: str, duration: str) -> Dict[str, Any]:
        """Generate a complete transcript using Azure OpenAI for the specified scenario."""
        
        synthetic_data = self.data_gen.generate_call_data(scenario)
        
        duration_minutes = self._parse_duration(duration)
        sentiment_type = self._parse_sentiment(sentiment)
        
        prompt = self.scenario_prompts[scenario](synthetic_data, sentiment_type, duration_minutes)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating realistic call center transcripts for medical scenarios. Generate natural, professional conversations that sound authentic. Always include speaker labels (Agent:, Dr. [Name]:, [Patient Name]:, etc.) and maintain consistency throughout the conversation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            transcript = response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating transcript with Azure OpenAI: {str(e)}")
        
        return {
            'transcript': transcript,
            'scenario': scenario,
            'sentiment': sentiment_type,
            'duration': f"{duration_minutes} minutes",
            'participants': self._extract_participants(transcript),
            'synthetic_data': synthetic_data,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'word_count': len(transcript.split()),
                'estimated_duration': duration_minutes,
                'generation_method': 'azure_openai'
            }
        }
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to minutes."""
        import random
        if duration.lower() == "short":
            return random.randint(1, 3)
        elif duration.lower() == "medium":
            return random.randint(3, 7)
        else:  # Long
            return random.randint(7, 15)
    
    def _parse_sentiment(self, sentiment: str) -> str:
        """Parse sentiment string."""
        import random
        if sentiment.lower() == "mixed":
            return random.choice(["positive", "neutral", "negative"])
        return sentiment.lower()
    
    def _extract_participants(self, transcript: str) -> List[str]:
        """Extract participant names from transcript."""
        participants = []
        lines = transcript.split('\n')
        for line in lines:
            if ':' in line:
                speaker = line.split(':')[0].strip()
                if speaker not in participants:
                    participants.append(speaker)
        return participants
    
    def _get_healthcare_provider_prompt(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate prompt for healthcare provider inquiry scenario."""
        
        return f"""
Create a realistic call center transcript for a healthcare provider inquiry scenario with the following details:

**Call Details:**
- Scenario: Healthcare provider calling about a patient encounter
- Sentiment: {sentiment}
- Duration: {duration} minutes
- Agent Name: {data['agent_name']}
- Provider: Dr. {data['provider_name']} from {data['facility_name']}
- Patient: {data['patient_name']} (DOB: {data['patient_dob']}, ID: {data['patient_id']})
- Visit Date: {data['visit_date']}
- Diagnosis: {data['diagnosis']}
- Medication: {data['medication']}

**Instructions:**
1. Start with a professional greeting from the agent
2. Have the doctor identify themselves and state their purpose
3. Include patient verification steps
4. Discuss the specific medical information relevant to the scenario
5. The conversation should reflect a {sentiment} tone throughout
6. Make the conversation approximately {duration} minutes long (aim for {duration * 150} words)
7. Include realistic medical terminology and procedures
8. End with appropriate closing remarks

**Sentiment Guidelines:**
- Positive: Smooth interaction, helpful agent, satisfied provider
- Negative: Delays, frustrations, system issues, escalations needed
- Neutral: Professional, straightforward, business-like interaction

Generate a natural, realistic transcript with proper speaker labels.
"""
    
    def _get_patient_visit_prompt(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate prompt for patient visit inquiry scenario."""
        
        return f"""
Create a realistic call center transcript for a patient visit inquiry scenario with the following details:

**Call Details:**
- Scenario: Patient calling about a recent visit
- Sentiment: {sentiment}
- Duration: {duration} minutes
- Agent Name: {data['agent_name']}
- Patient: {data['patient_name']} (DOB: {data['patient_dob']})
- Visit Date: {data['visit_date']}
- Facility: {data['facility_name']}
- Diagnosis: {data['diagnosis']}
- Provider: Dr. {data['provider_name']}
- Medication: {data['medication']}

**Instructions:**
1. Start with a professional greeting from the agent
2. Have the patient explain their reason for calling
3. Include patient verification steps
4. Discuss visit details, treatment, medications, or follow-up care
5. The conversation should reflect a {sentiment} tone throughout
6. Make the conversation approximately {duration} minutes long (aim for {duration * 150} words)
7. Include realistic patient concerns and medical information
8. End with appropriate closing remarks

**Sentiment Guidelines:**
- Positive: Satisfied patient, good experience, helpful information
- Negative: Complaints about service, billing issues, poor experience
- Neutral: Routine inquiry, straightforward questions, professional interaction

Generate a natural, realistic transcript with proper speaker labels.
"""
    
    def _get_caregiver_inquiry_prompt(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate prompt for caregiver inquiry scenario."""
        
        return f"""
Create a realistic call center transcript for a caregiver inquiry scenario with the following details:

**Call Details:**
- Scenario: Caregiver calling with medical questions
- Sentiment: {sentiment}
- Duration: {duration} minutes
- Agent Name: {data['agent_name']}
- Caregiver: {data['caregiver_name']} ({data['relationship']} of patient)
- Patient: {data['patient_name']} (DOB: {data['patient_dob']})
- Diagnosis: {data['diagnosis']}
- Medication: {data['medication']}
- Facility: {data['facility_name']}

**Instructions:**
1. Start with a professional greeting from the agent
2. Have the caregiver identify themselves and their relationship to the patient
3. Include patient verification and authorization steps
4. Discuss medical questions, care instructions, or concerns
5. The conversation should reflect a {sentiment} tone throughout
6. Make the conversation approximately {duration} minutes long (aim for {duration * 150} words)
7. Include realistic caregiver concerns and medical guidance
8. Address privacy/authorization requirements appropriately
9. End with appropriate closing remarks

**Sentiment Guidelines:**
- Positive: Helpful agent, clear information, satisfied caregiver
- Negative: Authorization issues, unclear information, frustrated caregiver
- Neutral: Professional inquiry, routine questions, standard procedures

Generate a natural, realistic transcript with proper speaker labels.
"""
    
    def save_transcript_to_file(self, transcript_data: Dict[str, Any], transcript_id: str, save_locally: bool = True) -> Dict[str, Any]:
        """Save transcript to file, matching the original interface."""
        import os
        
        content = f"""Contoso Call Center Transcript
Generated: {transcript_data['metadata']['generated_at']}
Scenario: {transcript_data['scenario']}
Sentiment: {transcript_data['sentiment']}
Duration: {transcript_data['duration']}
Participants: {', '.join(transcript_data['participants'])}
Generation Method: Azure OpenAI

==================================================

{transcript_data['transcript']}

==================================================

Disclaimer: This is a synthetic transcript generated for training and simulation purposes only. 
All patient information is fictitious and does not represent real individuals or medical records.
"""
        
        if save_locally:
            transcript_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'generated_transcripts')
            os.makedirs(transcript_dir, exist_ok=True)
            
            file_path = os.path.join(transcript_dir, f"{transcript_id}.txt")
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {'file_path': file_path, 'content': content}
            except Exception as e:
                return {'file_path': None, 'content': content, 'error': str(e)}
        else:
            return {'file_path': None, 'content': content}
