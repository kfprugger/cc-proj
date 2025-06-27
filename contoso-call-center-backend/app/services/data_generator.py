import random
from faker import Faker
from datetime import datetime, timedelta
from typing import Dict, List

class SyntheticDataGenerator:
    def __init__(self):
        self.fake = Faker()
        
        self.medical_conditions = [
            "Hypertension", "Type 2 Diabetes", "Asthma", "Arthritis", "Depression",
            "Anxiety", "Migraine", "Back Pain", "COPD", "Heart Disease",
            "Osteoporosis", "Fibromyalgia", "Sleep Apnea", "Allergic Rhinitis",
            "Gastroesophageal Reflux", "Hypothyroidism", "Chronic Fatigue Syndrome"
        ]
        
        self.medications = [
            "Lisinopril", "Metformin", "Albuterol", "Ibuprofen", "Sertraline",
            "Omeprazole", "Atorvastatin", "Levothyroxine", "Amlodipine", "Gabapentin",
            "Hydrochlorothiazide", "Losartan", "Prednisone", "Tramadol", "Fluoxetine"
        ]
        
        self.facilities = [
            "Contoso General Hospital", "Contoso Medical Center", "Contoso Emergency Care",
            "Contoso Family Clinic", "Contoso Urgent Care", "Contoso Specialty Center",
            "Contoso Women's Health", "Contoso Pediatric Center", "Contoso Cardiac Institute"
        ]
        
        self.provider_titles = ["Dr.", "Nurse", "PA", "NP"]
        self.relationships = ["mother", "father", "spouse", "daughter", "son", "sister", "brother", "guardian"]
    
    def generate_call_data(self, scenario: str) -> Dict:
        """Generate synthetic data for a specific call scenario."""
        
        base_data = {
            'agent_name': self.fake.first_name(),
            'patient_name': self.fake.name(),
            'patient_dob': self.fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%m/%d/%Y'),
            'patient_id': f"CTM{random.randint(100000, 999999)}",
            'visit_date': self.fake.date_between(start_date='-30d', end_date='today').strftime('%m/%d/%Y'),
            'diagnosis': random.choice(self.medical_conditions),
            'medication': random.choice(self.medications),
            'facility_name': random.choice(self.facilities),
            'provider_name': self.fake.last_name(),
            'phone_number': self.fake.phone_number(),
            'address': self.fake.address().replace('\n', ', ')
        }
        
        if scenario == 'healthcare_provider':
            base_data.update({
                'provider_title': random.choice(self.provider_titles),
                'provider_npi': f"{random.randint(1000000000, 9999999999)}",
                'referring_facility': random.choice(self.facilities)
            })
        
        elif scenario == 'caregiver_inquiry':
            base_data.update({
                'caregiver_name': self.fake.name(),
                'relationship': random.choice(self.relationships),
                'caregiver_phone': self.fake.phone_number()
            })
        
        base_data.update({
            'insurance_provider': random.choice([
                "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth",
                "Humana", "Kaiser Permanente", "Medicare", "Medicaid"
            ]),
            'policy_number': f"{random.choice(['BC', 'AE', 'CG', 'UH'])}{random.randint(100000000, 999999999)}",
            'group_number': f"GRP{random.randint(10000, 99999)}"
        })
        
        return base_data
