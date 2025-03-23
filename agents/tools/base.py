from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool, Tool
from pydantic import BaseModel, Field

# Import the tool functions but don't call them yet
from agents.tools.weather_tool import get_weather_tool
from agents.tools.search_tool import get_search_tool
from agents.tools.calculator_tool import get_calculator_tool

def get_tools(tool_names: List[str] = None) -> List[BaseTool]:
    """
    Return a list of tools based on tool names.
    If no tool_names provided, returns all available tools.
    
    Note: Tools are initialized only when requested to avoid API key errors
    when certain tools aren't being used.
    """
    # Define tool getter functions without calling them immediately
    tools_map = {
        "weather": get_weather_tool,
        "search": get_search_tool,
        "calculator": get_calculator_tool,
    }
    
    result = []
    
    if tool_names:
        # Only initialize the tools that are specifically requested
        for name in tool_names:
            if name in tools_map:
                result.append(tools_map[name]())
    else:
        # For backwards compatibility, if no tools specified, initialize all
        # This might raise errors if API keys aren't set for all tools
        try:
            result = [func() for func in tools_map.values()]
        except Exception as e:
            print(f"Warning: Error initializing all tools: {e}")
            print("Consider specifying only the tools you need with API keys configured.")
    
    return result 