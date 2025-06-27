# Contoso Call Center Synthetic Transcript and Audio Generator - Setup Guide

This guide provides step-by-step instructions for setting up and running the Contoso Call Center application on three different environments: Windows, Linux (Ubuntu), and Azure App Service.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Windows Setup](#windows-setup)
- [Linux (Ubuntu) Setup](#linux-ubuntu-setup)
- [Azure App Service Deployment](#azure-app-service-deployment)
- [Environment Variables](#environment-variables)
- [Testing the Application](#testing-the-application)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Services
- **Azure AI Speech Service**: You'll need an Azure Cognitive Services Speech resource
  - Endpoint: `https://westus3.api.cognitive.microsoft.com/` (or your region)
  - API Key: Required for text-to-speech functionality

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm** or **yarn**: For frontend package management

---

## Windows Setup

### 1. Install System Dependencies

#### Install Python
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### Install Node.js
1. Download Node.js 16+ from [nodejs.org](https://nodejs.org/)
2. Install with default settings
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

#### Install Git
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Install with default settings

### 2. Clone and Setup Backend

```cmd
# Clone the repository
git clone <repository-url>
cd contoso-call-center-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
```

### 3. Configure Environment Variables

Edit `.env` file in the backend directory:
```env
AZURE_SPEECH_KEY=your_azure_speech_api_key
AZURE_SPEECH_REGION=westus3
AZURE_SPEECH_ENDPOINT=https://westus3.api.cognitive.microsoft.com/
```

### 4. Setup Frontend

```cmd
# Navigate to frontend directory
cd ..\contoso-call-center-frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env
```

Edit `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

### 5. Run the Application

#### Start Backend (in one terminal)
```cmd
cd contoso-call-center-backend
venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Frontend (in another terminal)
```cmd
cd contoso-call-center-frontend
npm run dev
```

### 6. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Linux (Ubuntu) Setup

### 1. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Git
sudo apt install git -y

# Install ffmpeg (for audio processing)
sudo apt install ffmpeg -y

# Verify installations
python3 --version
pip3 --version
node --version
npm --version
git --version
ffmpeg -version
```

### 2. Clone and Setup Backend

```bash
# Clone the repository
git clone <repository-url>
cd contoso-call-center-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `.env` file in the backend directory:
```bash
nano .env
```

Add the following:
```env
AZURE_SPEECH_KEY=your_azure_speech_api_key
AZURE_SPEECH_REGION=westus3
AZURE_SPEECH_ENDPOINT=https://westus3.api.cognitive.microsoft.com/
```

### 4. Setup Frontend

```bash
# Navigate to frontend directory
cd ../contoso-call-center-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

Edit `.env` file in the frontend directory:
```bash
nano .env
```

Add the following:
```env
VITE_API_URL=http://localhost:8000
```

### 5. Run the Application

#### Start Backend (in one terminal)
```bash
cd contoso-call-center-backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Frontend (in another terminal)
```bash
cd contoso-call-center-frontend
npm run dev
```

### 6. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Azure App Service Deployment

### Prerequisites for Azure Deployment
- Azure CLI installed and configured
- Azure subscription with App Service plan
- Azure Cognitive Services Speech resource created

### 1. Prepare Backend for Deployment

#### Create `startup.sh` in backend root:
```bash
#!/bin/bash
cd /home/site/wwwroot
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Update `requirements.txt` to include production dependencies:
```txt
fastapi[standard]>=0.115.0
psycopg[binary]>=3.2.0
faker>=37.0.0
pydub>=0.25.0
ffmpeg-python>=0.2.0
numpy>=2.0.0
scipy>=1.14.0
python-multipart>=0.0.20
azure-cognitiveservices-speech>=1.44.0
python-dotenv>=1.0.0
gender-guesser>=0.4.0
uvicorn[standard]>=0.30.0
gunicorn>=21.2.0
```

### 2. Deploy Backend to Azure App Service

```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name contoso-call-center-rg --location "West US 3"

# Create App Service plan
az appservice plan create \
  --name contoso-call-center-plan \
  --resource-group contoso-call-center-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group contoso-call-center-rg \
  --plan contoso-call-center-plan \
  --name contoso-call-center-backend \
  --runtime "PYTHON|3.11" \
  --startup-file startup.sh

# Configure app settings
az webapp config appsettings set \
  --resource-group contoso-call-center-rg \
  --name contoso-call-center-backend \
  --settings \
    AZURE_SPEECH_KEY="your_azure_speech_api_key" \
    AZURE_SPEECH_REGION="westus3" \
    AZURE_SPEECH_ENDPOINT="https://westus3.api.cognitive.microsoft.com/" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Deploy code
cd contoso-call-center-backend
az webapp up \
  --resource-group contoso-call-center-rg \
  --name contoso-call-center-backend \
  --runtime "PYTHON|3.11"
```

### 3. Deploy Frontend

#### Build the frontend for production:
```bash
cd contoso-call-center-frontend

# Update .env for production
echo "VITE_API_URL=https://contoso-call-center-backend.azurewebsites.net" > .env

# Build the application
npm run build
```

#### Deploy to Azure Static Web Apps:
```bash
# Create static web app
az staticwebapp create \
  --name contoso-call-center-frontend \
  --resource-group contoso-call-center-rg \
  --source https://github.com/your-username/your-repo \
  --location "West US 2" \
  --branch main \
  --app-location "/contoso-call-center-frontend" \
  --output-location "dist"
```

### 4. Configure CORS on Backend

Add your frontend domain to CORS settings in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-static-web-app.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Access the Deployed Application
- Backend API: `https://contoso-call-center-backend.azurewebsites.net`
- Frontend: `https://your-static-web-app.azurestaticapps.net`
- API Documentation: `https://contoso-call-center-backend.azurewebsites.net/docs`

---

## Environment Variables

### Backend Environment Variables (.env)
```env
# Azure Speech Service Configuration
AZURE_SPEECH_KEY=your_azure_speech_api_key
AZURE_SPEECH_REGION=westus3
AZURE_SPEECH_ENDPOINT=https://westus3.api.cognitive.microsoft.com/

# Optional: Database configuration (if using external database)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Optional: Logging level
# LOG_LEVEL=INFO
```

### Frontend Environment Variables (.env)
```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# For production deployment
# VITE_API_URL=https://your-backend-domain.com
```

---

## Testing the Application

### 1. Health Check
Test the backend health endpoint:
```bash
curl http://localhost:8000/healthz
# Should return: {"status": "healthy"}
```

### 2. API Documentation
Visit the interactive API documentation:
- Local: http://localhost:8000/docs
- Production: https://your-backend-domain.com/docs

### 3. Generate Test Calls
1. Open the frontend application
2. Select a scenario (Healthcare Provider Inquiry, Patient Visit, or Caregiver Inquiry)
3. Configure sentiment and duration settings
4. Enable/disable audio generation and local file saving as needed
5. Click "Generate Calls"
6. Download generated transcripts and audio files

---

## Troubleshooting

### Common Issues

#### Windows: "python is not recognized"
- Ensure Python is added to PATH during installation
- Restart command prompt after installation
- Use `py` instead of `python` if needed

#### Linux: Permission denied errors
```bash
# Fix permissions for startup script
chmod +x startup.sh

# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
```

#### Audio Generation Issues
- **Windows**: The application includes a fallback method for systems without ffmpeg
- **Linux**: Ensure ffmpeg is installed: `sudo apt install ffmpeg`
- **Azure**: ffmpeg-python dependency should handle audio processing

#### CORS Errors
- Ensure backend CORS settings include your frontend domain
- Check that frontend is using the correct backend URL
- Verify both services are running on expected ports

#### Azure Deployment Issues
```bash
# Check deployment logs
az webapp log tail --resource-group contoso-call-center-rg --name contoso-call-center-backend

# Restart the app service
az webapp restart --resource-group contoso-call-center-rg --name contoso-call-center-backend
```

#### Memory Issues on Azure
- Consider upgrading to a higher App Service plan (B2 or higher)
- Monitor memory usage in Azure portal
- Optimize audio generation settings for lower memory usage

### Getting Help
- Check the application logs for detailed error messages
- Verify all environment variables are correctly set
- Ensure all dependencies are installed
- Test API endpoints individually using the `/docs` interface

---

## Additional Notes

### Security Considerations
- Never commit API keys to version control
- Use Azure Key Vault for production secrets
- Implement proper authentication for production deployments
- Configure network security groups for Azure resources

### Performance Optimization
- Consider using Azure CDN for frontend static assets
- Implement caching for frequently requested data
- Monitor Azure Application Insights for performance metrics
- Use Azure Storage for generated files in production

### Scaling Considerations
- Azure App Service can auto-scale based on demand
- Consider using Azure Service Bus for background processing
- Implement database connection pooling for high-traffic scenarios
- Use Azure Load Balancer for multiple backend instances
