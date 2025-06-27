import random
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from data_generator import SyntheticDataGenerator

class TranscriptGenerator:
    def __init__(self):
        self.data_gen = SyntheticDataGenerator()
        self.scenarios = {
            'healthcare_provider': self._generate_healthcare_provider_scenario,
            'patient_visit': self._generate_patient_visit_scenario,
            'caregiver_inquiry': self._generate_caregiver_inquiry_scenario
        }
    
    def generate_transcript(self, scenario: str, sentiment: str, duration: str) -> Dict[str, Any]:
        """Generate a complete transcript for the specified scenario."""
        
        synthetic_data = self.data_gen.generate_call_data(scenario)
        
        duration_minutes = self._parse_duration(duration)
        sentiment_type = self._parse_sentiment(sentiment)
        
        transcript = self.scenarios[scenario](synthetic_data, sentiment_type, duration_minutes)
        
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
                'estimated_duration': duration_minutes
            }
        }
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to minutes."""
        if "Short" in duration:
            return random.randint(1, 3)
        elif "Medium" in duration:
            return random.randint(3, 7)
        else:  # Long
            return random.randint(7, 15)
    
    def _parse_sentiment(self, sentiment: str) -> str:
        """Parse sentiment string."""
        if sentiment == "Mixed (Random)":
            return random.choice(["Positive", "Neutral", "Negative"])
        return sentiment
    
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
    
    def _generate_healthcare_provider_scenario(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate transcript for healthcare provider inquiry scenario."""
        
        provider_name = data['provider_name']
        patient_name = data['patient_name']
        patient_dob = data['patient_dob']
        patient_id = data['patient_id']
        visit_date = data['visit_date']
        diagnosis = data['diagnosis']
        
        transcript_parts = [
            f"Agent: Thank you for calling Contoso Medical, this is {data['agent_name']}. How can I help you today?",
            f"{provider_name}: Hi, this is Dr. {provider_name} from {data['facility_name']}. I'm calling about a patient encounter and need to verify some information.",
            f"Agent: Of course, Dr. {provider_name}. I'd be happy to help. Can you provide me with the patient's information?",
            f"{provider_name}: Yes, the patient's name is {patient_name}, date of birth {patient_dob}, and patient ID {patient_id}.",
            f"Agent: Thank you. Let me pull up that record... I see the patient here. What specific information do you need?",
            f"{provider_name}: I need to confirm the details from their visit on {visit_date}. We're reviewing the {diagnosis} diagnosis and treatment plan.",
        ]
        
        if sentiment == "Positive":
            transcript_parts.extend([
                f"Agent: Absolutely, I can see that visit. The patient was seen for {diagnosis} and the treatment plan was documented thoroughly.",
                f"{provider_name}: Perfect, that matches our records. The patient has been responding well to the treatment.",
                f"Agent: That's wonderful to hear. Is there anything else you need regarding this patient's care?",
                f"{provider_name}: No, that covers everything. Thank you for your help.",
                f"Agent: You're very welcome, Dr. {provider_name}. Have a great day!"
            ])
        elif sentiment == "Negative":
            transcript_parts.extend([
                f"Agent: I'm showing some discrepancies in the documentation. Let me transfer you to our medical records department.",
                f"{provider_name}: This is frustrating. I've been trying to get this information for days.",
                f"Agent: I sincerely apologize for the inconvenience. Let me see what I can do to expedite this.",
                f"{provider_name}: The patient's care is being delayed because of these documentation issues.",
                f"Agent: I understand your concern. I'm escalating this to our supervisor immediately.",
                f"{provider_name}: Please do. This needs to be resolved today.",
                f"Agent: Absolutely. You should receive a call back within the hour with a resolution."
            ])
        else:  # Neutral
            transcript_parts.extend([
                f"Agent: I can confirm the visit details. The patient was treated for {diagnosis} as documented.",
                f"{provider_name}: Good. I also need to verify the prescribed medications from that visit.",
                f"Agent: Let me check the medication list... I see {data['medication']} was prescribed.",
                f"{provider_name}: That's correct. Can you email me a copy of the complete visit summary?",
                f"Agent: Certainly. I'll send that to your registered email address within the next few minutes.",
                f"{provider_name}: Thank you. That should be everything I need.",
                f"Agent: You're welcome. Is there anything else I can help you with today?",
                f"{provider_name}: No, that covers it. Thank you for your assistance."
            ])
        
        return '\n'.join(transcript_parts)
    
    def _generate_patient_visit_scenario(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate transcript for patient visit inquiry scenario."""
        
        patient_name = data['patient_name']
        visit_date = data['visit_date']
        facility = data['facility_name']
        diagnosis = data['diagnosis']
        
        transcript_parts = [
            f"Agent: Good morning, Contoso Medical, this is {data['agent_name']}. How may I assist you?",
            f"{patient_name}: Hi, I'm calling about my recent visit to {facility} on {visit_date}.",
            f"Agent: Hello, {patient_name}. I'd be happy to help you with questions about your visit. Can you verify your date of birth for me?",
            f"{patient_name}: Yes, it's {data['patient_dob']}.",
            f"Agent: Thank you. I have your record here. What questions do you have about your visit?",
        ]
        
        if sentiment == "Positive":
            transcript_parts.extend([
                f"{patient_name}: I wanted to thank the staff for the excellent care I received. Everyone was so professional.",
                f"Agent: That's wonderful to hear! I'm so glad you had a positive experience with our team.",
                f"{patient_name}: The doctor explained everything clearly about my {diagnosis} and the treatment options.",
                f"Agent: Dr. {data['provider_name']} is excellent. Is there anything specific about your treatment plan you'd like to discuss?",
                f"{patient_name}: Actually, I'm feeling much better already. The medication is working well.",
                f"Agent: That's fantastic news! Please continue following the treatment plan as prescribed.",
                f"{patient_name}: I will. Thank you for everything.",
                f"Agent: You're very welcome. Don't hesitate to call if you have any other questions."
            ])
        elif sentiment == "Negative":
            transcript_parts.extend([
                f"{patient_name}: I'm very upset about my experience. I waited over three hours to be seen.",
                f"Agent: I'm so sorry to hear about the long wait time. That's definitely not the experience we want for our patients.",
                f"{patient_name}: And then the doctor seemed rushed and didn't explain my {diagnosis} properly.",
                f"Agent: I sincerely apologize. Let me connect you with our patient advocate to address these concerns.",
                f"{patient_name}: I also received a bill that seems incorrect. The charges don't match what I was told.",
                f"Agent: I understand your frustration. I'm going to have both our billing department and patient advocate reach out to you today.",
                f"{patient_name}: This whole experience has been disappointing. I expected better from Contoso Medical.",
                f"Agent: You have every right to be upset, and we're going to make this right. You'll hear from us within 24 hours."
            ])
        else:  # Neutral
            transcript_parts.extend([
                f"{patient_name}: I have some questions about the test results from my visit.",
                f"Agent: Of course. I can see you had some lab work done. What specific questions do you have?",
                f"{patient_name}: The doctor mentioned my {diagnosis} but I'd like to understand the next steps better.",
                f"Agent: Let me review your chart... I see you have a follow-up appointment scheduled. Would you like me to go over the treatment plan?",
                f"{patient_name}: Yes, that would be helpful. Also, when should I expect the prescription to start working?",
                f"Agent: Based on your medication, you should start seeing improvement within {random.randint(3, 14)} days.",
                f"{patient_name}: Okay, and what if I don't see improvement by then?",
                f"Agent: In that case, please call us or contact Dr. {data['provider_name']}'s office directly."
            ])
        
        return '\n'.join(transcript_parts)
    
    def _generate_caregiver_inquiry_scenario(self, data: Dict, sentiment: str, duration: int) -> str:
        """Generate transcript for caregiver inquiry scenario."""
        
        caregiver_name = data['caregiver_name']
        patient_name = data['patient_name']
        relationship = data['relationship']
        
        transcript_parts = [
            f"Agent: Contoso Medical, this is {data['agent_name']}. How can I help you today?",
            f"{caregiver_name}: Hello, I'm calling about my {relationship}, {patient_name}. I'm their primary caregiver.",
            f"Agent: Hi {caregiver_name}. I'd be happy to help. For privacy purposes, I'll need to verify that you're authorized to discuss this patient's information.",
            f"{caregiver_name}: Yes, I should be listed as an authorized contact. My name is {caregiver_name}.",
            f"Agent: Thank you. I can confirm you're listed as an authorized caregiver. What questions do you have?",
        ]
        
        if sentiment == "Positive":
            transcript_parts.extend([
                f"{caregiver_name}: I wanted to update you on {patient_name}'s progress. They're doing much better since starting the new treatment.",
                f"Agent: That's excellent news! I'm so glad to hear the treatment is working well.",
                f"{caregiver_name}: The physical therapy has really helped with their mobility, and their spirits are much higher.",
                f"Agent: Wonderful. Dr. {data['provider_name']} will be pleased to hear about this progress.",
                f"{caregiver_name}: Should we continue with the current treatment plan, or does anything need to be adjusted?",
                f"Agent: I'd recommend discussing any adjustments at your next scheduled appointment, but the current plan seems to be working well.",
                f"{caregiver_name}: Perfect. Thank you for all the support your team has provided.",
                f"Agent: It's our pleasure. Please don't hesitate to call if you have any other questions."
            ])
        elif sentiment == "Negative":
            transcript_parts.extend([
                f"{caregiver_name}: I'm very concerned about {patient_name}'s condition. They seem to be getting worse, not better.",
                f"Agent: I'm sorry to hear that. Can you tell me more about what changes you've noticed?",
                f"{caregiver_name}: The medication doesn't seem to be helping, and they're in more pain than before.",
                f"Agent: That's definitely concerning. Let me check when their last appointment was... I think we need to get them seen sooner.",
                f"{caregiver_name}: I've been trying to reach Dr. {data['provider_name']} for days but haven't heard back.",
                f"Agent: That's unacceptable. I'm going to escalate this immediately and have the doctor call you today.",
                f"{caregiver_name}: {patient_name} is suffering, and I feel like no one is listening to our concerns.",
                f"Agent: I hear you, and I'm going to make sure this gets the urgent attention it deserves. You'll hear from us within two hours."
            ])
        else:  # Neutral
            transcript_parts.extend([
                f"{caregiver_name}: I have some questions about {patient_name}'s medication schedule and dietary restrictions.",
                f"Agent: Of course. Let me pull up their current treatment plan. What specific questions do you have?",
                f"{caregiver_name}: The medication bottle says to take with food, but they have trouble eating in the mornings.",
                f"Agent: That's a good question. Let me check with the pharmacy about alternative timing options.",
                f"{caregiver_name}: Also, are there any foods they should avoid while on this medication?",
                f"Agent: I can see some dietary guidelines in their chart. Let me go over those with you...",
                f"{caregiver_name}: That's helpful. Should I be monitoring anything specific at home?",
                f"Agent: Yes, please watch for any changes in appetite, sleep patterns, or energy levels and report those to us."
            ])
        
        return '\n'.join(transcript_parts)
