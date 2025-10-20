import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to manage API keys and other settings."""
    
    # API Keys
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    
    # Default values for testing
    DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
    
    @classmethod
    def validate_keys(cls):
        """Validate that required API keys are present."""
        missing_keys = []
        
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your_groq_api_key_here":
            missing_keys.append("GROQ_API_KEY")
        
        if not cls.OPENWEATHER_API_KEY or cls.OPENWEATHER_API_KEY == "your_openweather_api_key_here":
            missing_keys.append("OPENWEATHER_API_KEY")
        
        return missing_keys