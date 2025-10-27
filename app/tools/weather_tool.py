import requests
import re
from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain_groq import ChatGroq
from app.config import Config

class WeatherTool(BaseTool):
    name: str = "weather"
    description: str = "Useful for getting weather information for a specific city"
    
    def _extract_city_smart(self, query: str) -> str:
        """Smartly extract city name from query using multiple approaches."""
        query_lower = query.lower().strip()
        
        # Method 1: Try using LLM to extract city name
        try:
            api_key = Config.GROQ_API_KEY
            if api_key and api_key != "your_groq_api_key_here":
                llm = ChatGroq(
                    temperature=0,
                    groq_api_key=api_key,
                    model_name=Config.DEFAULT_GROQ_MODEL
                )
                
                extraction_prompt = f"""Extract ONLY the city name from this query. Return just the city name, nothing else.
If there's a country or state mentioned, include it (e.g., "Paris, France" or "Portland, Oregon").

Query: {query}

City name:"""
                
                response = llm.invoke(extraction_prompt)
                extracted_city = response.content.strip()
                
                # Clean up the extracted city
                extracted_city = extracted_city.strip('"\'.,!?')
                
                # Validate it's not empty or too long (likely not a city)
                if extracted_city and len(extracted_city) < 100:
                    return extracted_city
        except Exception as e:
            print(f"LLM extraction failed: {e}")
        
        # Method 2: Pattern-based extraction
        patterns = [
            r"weather\s+in\s+([a-zA-Z\s,'-]+?)(?:\s*\?|$|\s+weather|\s+today|\s+now)",
            r"in\s+([a-zA-Z\s,'-]+?)(?:\s*\?|$|\s+weather|\s+today|\s+now)",
            r"(?:at|for)\s+([a-zA-Z\s,'-]+?)(?:\s*\?|$|\s+weather|\s+today|\s+now)",
            r"([a-zA-Z\s,'-]+?)'s\s+weather",
            r"temperature\s+in\s+([a-zA-Z\s,'-]+?)(?:\s*\?|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Clean up
                city = city.strip('"\'.,!?')
                city = re.sub(r'\s+', ' ', city)  # Normalize whitespace
                if city:
                    return city
        
        # Method 3: Remove common weather-related words and get what's left
        words_to_remove = [
            'what', 'is', 'the', 'weather', 'today', 'now', 'current',
            'temperature', 'in', 'at', 'for', 'like', 'how', 'whats',
            'tell', 'me', 'about', 'give', 'show', 'a', 'an'
        ]
        
        words = query_lower.split()
        city_words = [w for w in words if w.strip('.,!?\'"') not in words_to_remove]
        
        if city_words:
            city = ' '.join(city_words)
            city = city.strip('"\'.,!?')
            # Capitalize properly
            city = ' '.join(word.capitalize() for word in city.split())
            return city
        
        return "San Francisco"  # Default fallback
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool to get weather information."""
        # Extract city name using smart extraction
        city = self._extract_city_smart(query)
        
        # Get OpenWeatherMap API key from config
        api_key = Config.OPENWEATHER_API_KEY
        
        if not api_key or api_key == "your_openweather_api_key_here":
            # Return mock data if no API key is provided
            return f"It's sunny and 24°C in {city}."
        
        # Make API call to OpenWeatherMap
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                actual_city = data.get("name", city)
                return f"It's {description} and {temp}°C in {actual_city}."
            else:
                error_msg = data.get('message', 'Unknown error')
                return f"Could not get weather for '{city}'. Error: {error_msg}. Please check the city name."
                
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Asynchronous version of the tool."""
        return self._run(query, run_manager=run_manager)