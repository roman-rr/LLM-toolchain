from langchain_core.tools import Tool
import requests
import os
from typing import Optional

def get_weather(location: str) -> str:
    """Get the current weather in a given location"""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return "Error: Weather API key not found. Please set the WEATHER_API_KEY environment variable."
    
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": location,
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Extract relevant weather info
        location_name = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        
        return f"Weather in {location_name}, {country}: {condition}, {temp_c}°C ({temp_f}°F)"
    
    except Exception as e:
        return f"Error getting weather data: {str(e)}"

def get_weather_tool():
    """Create a weather tool"""
    return Tool(
        name="weather",
        func=get_weather,
        description="Useful for getting current weather information in a specific location. Input should be a city name or location."
    )