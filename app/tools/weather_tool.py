import requests
from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from app.config import Config

class WeatherTool(BaseTool):
    name: str = "weather"
    description: str = "Useful for getting weather information for a specific city"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool to get weather information."""
        # Extract city name from query (simple approach)
        query_lower = query.lower()
        
        # Simple parsing to extract city name - look for "in" or "at" keywords
        city = "San Francisco"  # default city
        if "in" in query_lower:
            city = query_lower.split("in")[1].strip()
        elif "at" in query_lower:
            city = query_lower.split("at")[1].strip()
        elif "for" in query_lower:
            city = query_lower.split("for")[1].strip()
        
        # Remove common words to get just the city name
        city = city.split("weather")[0].strip() if "weather" in city else city
        city = city.split("?")[0].strip()  # Remove question mark
        
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
                return f"It's {description} and {temp}°C in {city}."
            else:
                return f"Could not get weather for {city}. Error: {data.get('message', 'Unknown error')}"
                
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Asynchronous version of the tool."""
        return self._run(query, run_manager=run_manager)