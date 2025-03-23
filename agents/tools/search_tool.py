from langchain_core.tools import Tool
from langchain_community.utilities import SerpAPIWrapper

def get_search_tool():
    """Create a search tool using SerpAPI"""
    search = SerpAPIWrapper()
    
    return Tool(
        name="search",
        func=search.run,
        description="Useful for searching the internet to find information on current events, data, or answers to questions. Input should be a search query."
    ) 