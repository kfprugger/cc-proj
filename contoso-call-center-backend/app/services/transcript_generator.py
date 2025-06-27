import random
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from .data_generator import SyntheticDataGenerator

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
        if duration.lower() == "short":
            return random.randint(1, 3)
        elif duration.lower() == "medium":
            return random.randint(3, 7)
        else:  # Long
            return random.randint(7, 15)
    
    def _parse_sentiment(self, sentiment: str) -> str:
        """Parse sentiment string."""
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
            f"Dr. {provider_name}: Hi, this is Dr. {provider_name} from {data['facility_name']}. I'm calling about a patient encounter and need to verify some information.",
            f"Agent: Of course, Dr. {provider_name}. I'd be happy to help. Can you provide me with the patient's information?",
            f"Dr. {provider_name}: Yes, the patient's name is {patient_name}, date of birth {patient_dob}, and patient ID {patient_id}.",
            f"Agent: Thank you. Let me pull up that record... I see the patient here. What specific information do you need?",
            f"Dr. {provider_name}: I need to confirm the details from their visit on {visit_date}. We're reviewing the {diagnosis} diagnosis and treatment plan.",
        ]
        
        if sentiment == "positive":
            transcript_parts.extend([
                f"Agent: Absolutely, I can see that visit. The patient was seen for {diagnosis} and the treatment plan was documented thoroughly.",
                f"Dr. {provider_name}: Perfect, that matches our records. The patient has been responding well to the treatment.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: That's excellent news. I can see the follow-up notes indicate steady improvement.",
                    f"Dr. {provider_name}: Yes, we've been monitoring their progress closely. Can you confirm the lab results from that visit?",
                    f"Agent: Certainly. I see the lab work was completed on {visit_date}. The results show {random.choice(['normal values', 'improved markers', 'stable indicators'])}.",
                    f"Dr. {provider_name}: Good, that aligns with our clinical observations.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"Agent: I also notice there's a care coordination note. Would you like me to review that?",
                    f"Dr. {provider_name}: Yes, please. We're planning the next phase of treatment.",
                    f"Agent: The care team noted excellent patient compliance and recommended continuing the current protocol with minor adjustments.",
                    f"Dr. {provider_name}: That's very helpful. Can you also check if there are any pending referrals?",
                    f"Agent: Let me check... I see a referral to {random.choice(['cardiology', 'endocrinology', 'orthopedics'])} was processed last week.",
                    f"Dr. {provider_name}: Perfect. The patient mentioned they hadn't heard back yet.",
                    f"Agent: I can see it's scheduled for next Tuesday. I'll have our scheduling team send a confirmation.",
                ])
            
            transcript_parts.extend([
                f"Agent: Is there anything else you need regarding this patient's care?",
                f"Dr. {provider_name}: No, that covers everything. Thank you for your help.",
                f"Agent: You're very welcome, Dr. {provider_name}. Have a great day!"
            ])
            
        elif sentiment == "negative":
            transcript_parts.extend([
                f"Agent: I'm showing some discrepancies in the documentation. Let me transfer you to our medical records department.",
                f"Dr. {provider_name}: This is frustrating. I've been trying to get this information for days.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: I sincerely apologize for the inconvenience. Let me see what I can do to expedite this.",
                    f"Dr. {provider_name}: The patient's care is being delayed because of these documentation issues.",
                    f"Agent: I completely understand your frustration. This is unacceptable. Let me check with my supervisor right now.",
                    f"Dr. {provider_name}: I've called three times this week and keep getting transferred around.",
                    f"Agent: I'm so sorry about that experience. I'm going to stay on this call until we get this resolved.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"Dr. {provider_name}: The patient has a follow-up appointment tomorrow and I need these records.",
                    f"Agent: I understand the urgency. Let me conference in our medical records supervisor immediately.",
                    f"Agent: [Brief hold] Dr. {provider_name}, I have our supervisor on the line. They're pulling the records now.",
                    f"Dr. {provider_name}: Finally. This should have been resolved days ago.",
                    f"Agent: You're absolutely right. We're implementing a new process to prevent this from happening again.",
                    f"Dr. {provider_name}: I hope so. This reflects poorly on patient care coordination.",
                    f"Agent: I agree completely. We're taking this very seriously and will follow up with you personally.",
                ])
            
            transcript_parts.extend([
                f"Agent: I'm escalating this to our supervisor immediately.",
                f"Dr. {provider_name}: Please do. This needs to be resolved today.",
                f"Agent: Absolutely. You should receive a call back within the hour with a resolution."
            ])
            
        else:  # Neutral
            transcript_parts.extend([
                f"Agent: I can confirm the visit details. The patient was treated for {diagnosis} as documented.",
                f"Dr. {provider_name}: Good. I also need to verify the prescribed medications from that visit.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: Let me check the medication list... I see {data['medication']} was prescribed.",
                    f"Dr. {provider_name}: That's correct. Can you also check the dosage and frequency?",
                    f"Agent: Yes, it shows {random.choice(['twice daily', 'once daily', 'three times daily'])} with {random.choice(['food', 'water', 'as needed'])}.",
                    f"Dr. {provider_name}: Good. Were there any drug interaction warnings noted?",
                    f"Agent: Let me check... No interaction warnings were flagged in the system.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"Dr. {provider_name}: I also need to review the discharge instructions that were given.",
                    f"Agent: Certainly. The discharge notes indicate standard post-treatment care with follow-up in {random.randint(1, 4)} weeks.",
                    f"Dr. {provider_name}: Was physical therapy recommended?",
                    f"Agent: Yes, I see a PT referral was made. The patient should have received those instructions.",
                    f"Dr. {provider_name}: Perfect. Can you email me a complete summary of the visit?",
                    f"Agent: Of course. I'll include the visit notes, medications, and all referrals.",
                    f"Dr. {provider_name}: That would be very helpful for our records.",
                ])
            
            transcript_parts.extend([
                f"Agent: Can you email me a copy of the complete visit summary?",
                f"Dr. {provider_name}: Certainly. I'll send that to your registered email address within the next few minutes.",
                f"Agent: You're welcome. Is there anything else I can help you with today?",
                f"Dr. {provider_name}: No, that covers it. Thank you for your assistance."
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
        
        if sentiment == "positive":
            transcript_parts.extend([
                f"{patient_name}: I wanted to thank the staff for the excellent care I received. Everyone was so professional.",
                f"Agent: That's wonderful to hear! I'm so glad you had a positive experience with our team.",
                f"{patient_name}: The doctor explained everything clearly about my {diagnosis} and the treatment options.",
                f"Agent: Dr. {data['provider_name']} is excellent. Is there anything specific about your treatment plan you'd like to discuss?",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"{patient_name}: Actually, I'm feeling much better already. The medication is working well.",
                    f"Agent: That's fantastic news! How long have you been on the medication?",
                    f"{patient_name}: About a week now, and the symptoms have really improved.",
                    f"Agent: Excellent! That's exactly what we like to hear. Are you experiencing any side effects?",
                    f"{patient_name}: None at all. I was worried about that, but everything has been smooth.",
                    f"Agent: Perfect. I can see in your notes that Dr. {data['provider_name']} expected good results with this treatment approach.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{patient_name}: I also wanted to ask about the follow-up care. When should I schedule my next appointment?",
                    f"Agent: Let me check your treatment plan... I see you're scheduled for a follow-up in 4 weeks, but we can adjust that if needed.",
                    f"{patient_name}: That sounds good. Will I need more lab work done?",
                    f"Agent: Yes, we'll want to check your levels to make sure the medication is working optimally and not causing any issues.",
                    f"{patient_name}: Makes sense. Can I schedule that lab work now?",
                    f"Agent: Absolutely! I can schedule that for the day before your appointment. How does next Wednesday at 9 AM work?",
                    f"{patient_name}: Perfect. And if I have questions before then, should I call this number?",
                    f"Agent: Yes, or you can also reach out to Dr. {data['provider_name']}'s office directly. They have your complete file.",
                ])
            
            transcript_parts.extend([
                f"Agent: Please continue following the treatment plan as prescribed.",
                f"{patient_name}: I will. Thank you for everything.",
                f"Agent: You're very welcome. Don't hesitate to call if you have any other questions."
            ])
            
        elif sentiment == "negative":
            transcript_parts.extend([
                f"{patient_name}: I'm very upset about my experience. I waited over three hours to be seen.",
                f"Agent: I'm so sorry to hear about the long wait time. That's definitely not the experience we want for our patients.",
                f"{patient_name}: And then the doctor seemed rushed and didn't explain my {diagnosis} properly.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: I sincerely apologize. That's completely unacceptable. Can you tell me more about what happened during your visit?",
                    f"{patient_name}: The doctor barely looked at me, spent maybe 5 minutes total, and I left with more questions than answers.",
                    f"Agent: This is very concerning. I'm going to document all of this and have our patient advocate reach out to you immediately.",
                    f"{patient_name}: I also received a bill that seems incorrect. The charges don't match what I was told.",
                    f"Agent: I understand your frustration completely. Let me get our billing department involved as well.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{patient_name}: This whole experience has been disappointing. I expected better from Contoso Medical.",
                    f"Agent: You have every right to be upset. This is not the standard of care we strive for.",
                    f"{patient_name}: I'm considering switching to a different provider. This has shaken my confidence.",
                    f"Agent: I completely understand that feeling. Before you make that decision, please let us try to make this right.",
                    f"{patient_name}: What exactly are you going to do? I've heard promises before.",
                    f"Agent: I'm escalating this to our medical director and patient advocate immediately. You'll hear from both of them today.",
                    f"{patient_name}: And what about the billing issue?",
                    f"Agent: Our billing manager will review your account and call you within 2 hours to resolve any discrepancies.",
                ])
            
            transcript_parts.extend([
                f"Agent: I'm going to have both our billing department and patient advocate reach out to you today.",
                f"{patient_name}: This whole experience has been disappointing. I expected better from Contoso Medical.",
                f"Agent: You have every right to be upset, and we're going to make this right. You'll hear from us within 24 hours."
            ])
            
        else:  # Neutral
            transcript_parts.extend([
                f"{patient_name}: I have some questions about the test results from my visit.",
                f"Agent: Of course. I can see you had some lab work done. What specific questions do you have?",
                f"{patient_name}: The doctor mentioned my {diagnosis} but I'd like to understand the next steps better.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: Let me review your chart in detail... I see you have a follow-up appointment scheduled. Would you like me to go over the treatment plan?",
                    f"{patient_name}: Yes, that would be helpful. Also, when should I expect the prescription to start working?",
                    f"Agent: Based on your medication, you should start seeing improvement within {random.randint(3, 14)} days.",
                    f"{patient_name}: And what should I do if I don't see improvement by then?",
                    f"Agent: In that case, please call us or contact Dr. {data['provider_name']}'s office directly to discuss adjusting the treatment.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{patient_name}: Are there any lifestyle changes I should make while on this medication?",
                    f"Agent: Good question. Let me check your discharge instructions... I see recommendations for {random.choice(['regular exercise', 'dietary modifications', 'stress management'])}.",
                    f"{patient_name}: What about interactions with other medications I'm taking?",
                    f"Agent: I can see your current medication list, and there don't appear to be any concerning interactions, but always check with your pharmacist.",
                    f"{patient_name}: Should I be monitoring anything specific at home?",
                    f"Agent: Yes, please keep track of your symptoms and any side effects. We've provided you with a symptom diary.",
                    f"{patient_name}: I don't think I received that. Can you send me one?",
                    f"Agent: Absolutely. I'll email that to you right after this call, along with a summary of today's discussion.",
                ])
            
            transcript_parts.extend([
                f"Agent: Is there anything else about your treatment plan you'd like to discuss?",
                f"{patient_name}: I think that covers everything for now. Thank you for taking the time to explain.",
                f"Agent: You're very welcome. Please don't hesitate to call if you have any other questions."
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
        
        if sentiment == "positive":
            transcript_parts.extend([
                f"{caregiver_name}: I wanted to update you on {patient_name}'s progress. They're doing much better since starting the new treatment.",
                f"Agent: That's excellent news! I'm so glad to hear the treatment is working well.",
                f"{caregiver_name}: The physical therapy has really helped with their mobility, and their spirits are much higher.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: Wonderful. Dr. {data['provider_name']} will be pleased to hear about this progress. How are they managing with daily activities?",
                    f"{caregiver_name}: Much better! They can walk to the kitchen on their own now, and they're sleeping through the night again.",
                    f"Agent: That's fantastic progress. Are they keeping up with their medication schedule?",
                    f"{caregiver_name}: Yes, we have a system set up and they haven't missed a dose. Should we continue with the current treatment plan?",
                    f"Agent: Based on this positive response, I'd recommend staying with the current plan, but let's discuss any adjustments at the next appointment.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{caregiver_name}: I also wanted to ask about the home health aide services. Are those still covered?",
                    f"Agent: Let me check your benefits... Yes, you're approved for 20 hours per week of home health aide services.",
                    f"{caregiver_name}: Great. And what about the medical equipment we discussed - the walker and shower chair?",
                    f"Agent: I can see those were approved as well. Have you received them yet?",
                    f"{caregiver_name}: The walker arrived, but we're still waiting on the shower chair.",
                    f"Agent: Let me check on that order... I see it was delayed. I'll expedite that and you should receive it by Friday.",
                    f"{caregiver_name}: Thank you so much. This equipment really makes a difference in their independence.",
                    f"Agent: Absolutely. Independence and safety are our top priorities for home care.",
                ])
            
            transcript_parts.extend([
                f"Agent: Perfect. Thank you for all the support your team has provided.",
                f"{caregiver_name}: It's our pleasure. Please don't hesitate to call if you have any other questions."
            ])
            
        elif sentiment == "negative":
            transcript_parts.extend([
                f"{caregiver_name}: I'm very concerned about {patient_name}'s condition. They seem to be getting worse, not better.",
                f"Agent: I'm sorry to hear that. Can you tell me more about what changes you've noticed?",
                f"{caregiver_name}: The medication doesn't seem to be helping, and they're in more pain than before.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: That's definitely concerning. How long have they been on the current medication?",
                    f"{caregiver_name}: About three weeks now, and if anything, the symptoms are getting worse.",
                    f"Agent: That's not what we want to hear at all. Are they experiencing any new symptoms or side effects?",
                    f"{caregiver_name}: Yes, they're having trouble sleeping, loss of appetite, and seem more confused than usual.",
                    f"Agent: These are serious concerns. Let me check when their last appointment was... I think we need to get them seen immediately.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{caregiver_name}: I've been trying to reach Dr. {data['provider_name']} for days but haven't heard back.",
                    f"Agent: That's completely unacceptable. You should never have to wait that long for a response about concerning symptoms.",
                    f"{caregiver_name}: {patient_name} is suffering, and I feel like no one is listening to our concerns.",
                    f"Agent: I hear you loud and clear, and I'm going to make sure this gets the urgent attention it deserves.",
                    f"{caregiver_name}: I'm at my wit's end. I don't know what else to do to help them.",
                    f"Agent: You're doing everything right by advocating for them. I'm escalating this to our medical director right now.",
                    f"{caregiver_name}: Should I take them to the emergency room? I'm really worried.",
                    f"Agent: If you're concerned about their immediate safety, yes. But I'm also having Dr. {data['provider_name']} call you within the hour.",
                ])
            
            transcript_parts.extend([
                f"Agent: That's unacceptable. I'm going to escalate this immediately and have the doctor call you today.",
                f"{caregiver_name}: {patient_name} is suffering, and I feel like no one is listening to our concerns.",
                f"Agent: I hear you, and I'm going to make sure this gets the urgent attention it deserves. You'll hear from us within two hours."
            ])
            
        else:  # Neutral
            transcript_parts.extend([
                f"{caregiver_name}: I have some questions about {patient_name}'s medication schedule and dietary restrictions.",
                f"Agent: Of course. Let me pull up their current treatment plan. What specific questions do you have?",
                f"{caregiver_name}: The medication bottle says to take with food, but they have trouble eating in the mornings.",
            ])
            
            if duration >= 3:  # Medium/Long duration
                transcript_parts.extend([
                    f"Agent: That's a good question. Let me check with the pharmacy about alternative timing options.",
                    f"{caregiver_name}: Also, are there any foods they should avoid while on this medication?",
                    f"Agent: I can see some dietary guidelines in their chart. Let me go over those with you...",
                    f"{caregiver_name}: They're also having trouble remembering to take their medications. Any suggestions?",
                    f"Agent: We have several options - pill organizers, medication reminder apps, or even automated dispensers.",
                ])
            
            if duration >= 7:  # Long duration only
                transcript_parts.extend([
                    f"{caregiver_name}: That's helpful. Should I be monitoring anything specific at home?",
                    f"Agent: Yes, please watch for any changes in appetite, sleep patterns, or energy levels and report those to us.",
                    f"{caregiver_name}: What about their mobility? They seem to be moving more slowly lately.",
                    f"Agent: That could be related to their condition or medication. Let's schedule a physical therapy evaluation.",
                    f"{caregiver_name}: Good idea. Can you also check if they're due for any lab work?",
                    f"Agent: Let me check... Yes, they're due for blood work next week. I can schedule that now if you'd like.",
                    f"{caregiver_name}: That would be great. And should I bring them in, or can someone come to the house?",
                    f"Agent: We have mobile lab services available. I can arrange for someone to come to your home.",
                ])
            
            transcript_parts.extend([
                f"Agent: Is there anything else about their care plan you'd like to discuss?",
                f"{caregiver_name}: I think that covers my main concerns for now. Thank you for being so thorough.",
                f"Agent: You're very welcome. Caregivers like you make such a difference in patient outcomes."
            ])
        
        return '\n'.join(transcript_parts)
    
    def save_transcript_to_file(self, transcript_data: Dict[str, Any], transcript_id: str, save_locally: bool = True) -> Dict[str, Any]:
        """Save transcript to file if save_locally=True and return transcript info with content."""
        import os
        
        content = f"Contoso Call Center Transcript\n"
        content += f"Generated: {transcript_data['metadata']['generated_at']}\n"
        content += f"Scenario: {transcript_data['scenario']}\n"
        content += f"Sentiment: {transcript_data['sentiment']}\n"
        content += f"Duration: {transcript_data['duration']}\n"
        content += f"Participants: {', '.join(transcript_data['participants'])}\n"
        content += f"\n{'='*50}\n\n"
        content += transcript_data['transcript']
        
        result = {
            'transcript_id': transcript_id,
            'content': content,
            'file_path': None
        }
        
        if save_locally:
            transcript_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_transcripts')
            os.makedirs(transcript_dir, exist_ok=True)
            
            file_path = os.path.join(transcript_dir, f"{transcript_id}.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result['file_path'] = file_path
        
        return result
