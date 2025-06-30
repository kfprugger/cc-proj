import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def test_azure_openai_setup():
    """Test Azure OpenAI setup and basic functionality."""
    print("Testing Azure OpenAI setup...")
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print(f"API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    
    if not all([api_key, endpoint, deployment]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        from app.services.azure_openai_generator import AzureOpenAITranscriptGenerator
        print("✓ Successfully imported AzureOpenAITranscriptGenerator")
        
        generator = AzureOpenAITranscriptGenerator()
        print("✓ Successfully initialized Azure OpenAI generator")
        
        print("\nTesting transcript generation...")
        result = generator.generate_transcript(
            scenario="healthcare_provider",
            sentiment="positive", 
            duration="short"
        )
        
        print("✓ Successfully generated transcript")
        print(f"Transcript length: {len(result['transcript'])} characters")
        print(f"Participants: {result['participants']}")
        print(f"Generation method: {result['metadata']['generation_method']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_azure_openai_setup()
    if success:
        print("\n🎉 Azure OpenAI integration test passed!")
    else:
        print("\n💥 Azure OpenAI integration test failed!")
        sys.exit(1)
