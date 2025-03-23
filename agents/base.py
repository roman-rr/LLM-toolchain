from typing import List, Dict, Any, Optional, Union, Callable
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage, BaseMessage
)

class BaseAgent:
    """Base agent class that other agents should inherit from"""
    
    def __init__(
        self, 
        llm: BaseLanguageModel,
        tools: List[BaseTool] = None,
        system_message: str = "You are a helpful AI assistant.",
    ):
        self.llm = llm
        self.tools = tools or []
        self.system_message = system_message
        
    def run(self, user_input: str) -> Dict[str, Any]:
        """Run the agent on user input"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def stream(self, user_input: str):
        """Stream the agent's response"""
        raise NotImplementedError("Subclasses must implement this method") 