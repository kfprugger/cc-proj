# Contoso Call Center Synthetic Transcript and Audio Generator

A Python-based application that generates synthetic call center conversations and corresponding audio files for medical scenarios. This tool simulates realistic interactions between call center agents and customers/patients for Contoso Medical, a fictitious medical company.

## 🎯 Purpose

This application is designed for training, testing, and demonstration purposes in healthcare call center environments. It generates realistic but completely synthetic conversations that can be used for:

- Call center agent training
- Quality assurance testing
- Speech recognition system testing
- Customer service workflow development
- Compliance and documentation training

## ✨ Features

### 📞 Call Scenarios
- **Healthcare Provider Inquiries**: Doctors calling about patient encounters
- **Patient Visit Follow-ups**: Patients calling about recent hospital/clinic visits
- **Caregiver Medical Questions**: Caregivers calling with questions about patients under care

### 🎭 Conversation Variety
- **Mixed Sentiment Support**: Positive, neutral, and negative conversation tones
- **Realistic PHI/PII Generation**: Synthetic but believable patient information
- **Variable Call Duration**: Short (1-3 min), Medium (3-7 min), Long (7-15 min)

### 🔊 Audio Generation
- **Azure AI Speech Integration**: High-quality text-to-speech synthesis
- **Gender-Appropriate Voices**: Automatic voice selection based on generated names
- **Configurable Audio Settings**:
  - Sampling Rate: 8 kHz, 16 kHz, 32 kHz, or 48 kHz
  - Channels: Mono or Stereo
  - Format: WAV (Microsoft PCM, 16-bit)
  - Bitrate: 256 kbps (mono), 512 kbps (stereo)

### 🖥️ User Interface
- **Intuitive Web Interface**: React-based frontend with modern UI
- **Scenario Selection**: Choose one or multiple call scenarios
- **Audio Controls**: Toggle audio generation on/off
- **Batch Generation**: Generate multiple calls simultaneously
- **Export Options**: Download transcripts (.txt) and audio files (.wav)

## 🏗️ Architecture

### Backend (FastAPI)
- **API Endpoints**: RESTful API for call generation
- **Transcript Generation**: Intelligent conversation flow creation
- **Audio Processing**: Azure Speech SDK integration
- **File Management**: Organized storage of generated content

### Frontend (React + TypeScript)
- **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- **Real-time Updates**: Live generation progress tracking
- **Responsive Design**: Works on desktop and mobile devices
- **Download Management**: Easy access to generated files

## 📁 Project Structure

```
cc-proj/
├── contoso-call-center-backend/     # FastAPI backend
│   ├── app/
│   │   ├── main.py                  # FastAPI application
│   │   ├── models.py                # Data models
│   │   └── services/
│   │       ├── transcript_generator.py  # Conversation generation
│   │       ├── audio_generator.py       # Azure Speech integration
│   │       └── data_generator.py        # Synthetic data creation
│   ├── generated_audio/             # Generated .wav files
│   ├── generated_transcripts/       # Generated .txt files
│   └── pyproject.toml              # Python dependencies
├── contoso-call-center-frontend/    # React frontend
│   ├── src/
│   │   ├── App.tsx                 # Main application component
│   │   └── components/             # UI components
│   └── package.json                # Node.js dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Azure Speech Services API key

### Backend Setup
```bash
cd contoso-call-center-backend
poetry install
cp .env.example .env
# Add your Azure Speech API key to .env
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd contoso-call-center-frontend
npm install
npm run dev
```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
SPEECH_KEY=your_azure_speech_api_key
SPEECH_REGION=your_azure_region
```

### Audio Settings
Configure audio output through the web interface:
- **Sampling Rate**: Choose based on your quality requirements
- **Channels**: Mono recommended for call center scenarios
- **Duration**: Select based on training needs

## 📊 Generated Content

### Transcript Format
```
Contoso Call Center Transcript
Generated: 2025-06-27T18:45:56
Scenario: healthcare_provider
Sentiment: positive
Duration: 6 minutes
Participants: Agent, Dr. Smith

==================================================

Agent: Thank you for calling Contoso Medical, this is Sarah...
Dr. Smith: Hi Sarah, this is Dr. Smith from General Hospital...
```

### Audio Files
- **Naming Convention**: `contoso_call_YYYYMMDD_HHMMSS_call_N.wav`
- **Storage Location**: `generated_audio/` directory
- **Quality**: Professional-grade speech synthesis
- **Voice Variety**: Different voices for agents and callers

## 🛡️ Privacy & Compliance

- **100% Synthetic Data**: All patient information is computer-generated
- **No Real PHI/PII**: Compliant with healthcare privacy regulations
- **Training Safe**: Designed specifically for educational purposes
- **Disclaimer Included**: All generated content marked as fictitious

## 🔍 Use Cases

### Training Scenarios
- New agent onboarding
- Difficult conversation handling
- Medical terminology practice
- Compliance procedure training

### Testing Applications
- Speech recognition accuracy testing
- Call routing system validation
- Quality assurance workflow testing
- Customer satisfaction measurement

### Development Support
- API integration testing
- User interface development
- Performance benchmarking
- System load testing

## 🤝 Contributing

This application was developed for Contoso Medical's internal training and testing needs. For modifications or enhancements, please follow standard development practices and ensure all generated content remains synthetic and compliant.

## ⚠️ Important Disclaimers

- **Synthetic Data Only**: All patient information is computer-generated and fictitious
- **Training Purpose**: Designed exclusively for educational and testing scenarios
- **No Real Medical Data**: Does not contain or process actual patient information
- **Compliance**: Maintains healthcare privacy standards through synthetic data generation

## 📞 Support

For technical support or questions about the Contoso Call Center Synthetic Transcript and Audio Generator, please refer to the API documentation at `/docs` when running the backend server.

---

*Generated content is for simulation and training purposes only. All patient data is synthetic and fictitious.*
