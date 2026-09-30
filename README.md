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
- **Azure AI Speech Integration**: High-quality text-to-speech synthesis with dual implementation options
- **Azure Speech Batch API**: Server-side audio concatenation for improved performance (configurable)
- **Standard Audio Generation**: Local pydub-based audio stitching (fallback option)
- **Multi-Voice SSML Support**: Automatic speaker detection and voice assignment
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
- Python 3.12 (the verified audio runtime)
- Poetry 2.5 or newer
- Node.js 22 or newer
- Azure Speech Services and Azure OpenAI credentials for cloud generation

### Backend Setup
```bash
cd contoso-call-center-backend
poetry sync
# Configure .env with the Azure Speech and Azure OpenAI settings below.
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd contoso-call-center-frontend
npm ci
npm run dev
```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Dependency maintenance

The September 2026 security update upgrades FastAPI to the 0.133 release line,
which supports patched Starlette 1.x. The backend declares security minimums for
Starlette, AnyIO, Click, multipart parsing, dotenv, and Requests. The Poetry lock
also updates Azure Core, urllib3, IDNA, and Pygments. The frontend uses Vite 6.4.3
and patched transitive dependencies without changing its React version.

Commit `poetry.lock` and `package-lock.json` with dependency changes. Generate
them with Poetry and npm, rather than editing lock entries. Use the lockfiles for
reproducible installs; `requirements.txt` retains compatible security minimums
for environments that install with pip.

Local checks are `poetry check --lock`, `poetry run python test_batch_audio.py`,
`npm run build`, and `npm run lint` in their respective backend/frontend folders.
The batch-audio check exercises SSML and transcript parsing without synthesizing
cloud audio. The API's health, scenarios, request validation, CORS, transcript
downloads, and unavailable-service error handling can also be checked locally.
Successful cloud transcript and audio generation still requires valid Azure
credentials and deployments; offline checks do not verify those services.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
# Azure Speech Services Configuration
SPEECH_KEY=your_azure_speech_api_key
SPEECH_REGION=your_azure_region

# Audio Generation Mode (optional)
USE_BATCH_AUDIO=false  # Set to 'true' to enable Azure Batch TTS API

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### Azure Batch TTS Configuration
The application supports two audio generation modes:

**Standard Mode (Default):**
- Uses Azure Speech SDK with local pydub audio stitching
- Reliable fallback option with proven performance
- Set `USE_BATCH_AUDIO=false` or omit the variable

**Batch Mode (Advanced):**
- Uses Azure Speech Batch API for server-side audio concatenation
- Improved performance through single API call
- Multi-voice SSML with automatic speaker detection
- Set `USE_BATCH_AUDIO=true` to enable
- Gracefully falls back to standard mode on API errors

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
