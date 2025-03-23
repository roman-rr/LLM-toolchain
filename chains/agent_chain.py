from typing import Dict, List, Any, Optional, Union, Callable
import uuid
import os

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from agents.tools.base import get_tools
from models.llms import get_openai_chat_model
from chat_history.base import ChatManager
from graphs.react_agent import create_agent_with_chat_history
from graphs.conversational_agent import create_conversational_agent_with_chat_history

from dotenv import load_dotenv
load_dotenv()

def create_chain(
    thread_id: str = None,
    agent_type: str = "react",  # "react" or "conversational"
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    tools: List[str] = None,
    connection_string: Optional[str] = None,
    table_name: str = "message_store",
    system_message: str = None,
    streaming: bool = False,
) -> Dict[str, Any]:
    """
    Create an agent chain with chat history persistence.
    
    Args:
        thread_id: Unique identifier for this conversation thread (UUID string)
        agent_type: Type of agent to create ("react" or "conversational")
        model_name: Name of the language model to use
        temperature: Temperature setting for the language model
        tools: List of tool names to include (if None, uses default tools)
        connection_string: PostgreSQL connection string (defaults to POSTGRES_URI env var)
        table_name: Name of the table to store messages
        system_message: System message to use in the conversations
        streaming: Whether to use streaming by default
        
    Returns:
        A function that accepts a message and returns a response
    """
    # Generate a UUID if none provided
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Ensure thread_id is a valid UUID
    try:
        uuid.UUID(thread_id)
    except ValueError:
        # If not a valid UUID, generate a new one
        thread_id = str(uuid.uuid4())
    
    print(f"Thread ID: {thread_id}")
    
    # Get connection string from environment if not provided
    if not connection_string:
        connection_string = os.environ.get("POSTGRES_URI")
        if not connection_string:
            raise ValueError("No PostgreSQL connection string provided. Set POSTGRES_URI environment variable or pass connection_string.")
    
    # Create a single database connection
    import psycopg
    connection = psycopg.connect(connection_string)
    
    # Get the appropriate model
    if "gpt" in model_name.lower():
        llm = get_openai_chat_model(model_name=model_name, temperature=temperature)
    else:
        raise ValueError(f"Unsupported model name: {model_name}")
    
    # Get tools
    tool_list = get_tools(tools)
    
    # Create chat manager with the established connection
    chat_manager = ChatManager(
        llm=llm,
        connection_string=connection_string,
        connection=connection,
        table_name=table_name,
        system_message=system_message or "You are a helpful AI assistant."
    )
    
    # Create the appropriate agent
    if agent_type.lower() == "react":
        agent_functions = create_agent_with_chat_history(
            llm=llm,
            tools=tool_list,
            thread_id=thread_id,
            chat_manager=chat_manager,
            system_message=system_message,
        )
    elif agent_type.lower() == "conversational":
        agent_functions = create_conversational_agent_with_chat_history(
            llm=llm,
            tools=tool_list,
            thread_id=thread_id,
            chat_manager=chat_manager,
            system_message=system_message,
        )
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")
    
    # Define the chain function based on streaming preference
    def chain_func(message: str, use_streaming: bool = None) -> Dict[str, Any]:
        use_stream = streaming if use_streaming is None else use_streaming
        
        if use_stream:
            return agent_functions["stream"](message)
        else:
            return agent_functions["run"](message)
    
    # Add helper methods to the function for additional operations
    chain_func.get_history = lambda: chat_manager.get_message_history(thread_id)
    chain_func.clear_history = lambda: chat_manager.clear_history(thread_id)
    chain_func.thread_id = thread_id
    
    # Define the cleanup function to close connection when done
    def cleanup():
        connection.close()
    
    # Add cleanup method to the function
    chain_func.cleanup = cleanup
    
    return chain_func 