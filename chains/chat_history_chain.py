import os
import uuid
from typing import Optional, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain

from chat_history.base import ChatManager
from chat_history.memory import get_message_history, create_memory
from models.llms import get_openai_chat_model

from dotenv import load_dotenv
load_dotenv()

def create_chain(
    thread_id: str = None,  # Changed from "default" to None 
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    connection_string: Optional[str] = None,
    table_name: str = "message_store",
    system_message: str = "You are a helpful assistant.",
    language: str = "English",
    streaming: bool = False,
) -> Dict[str, Any]:
    """
    Create a chat history chain for conversation with persistence.
    
    Args:
        thread_id: Unique identifier for this conversation thread (UUID string)
        model_name: Name of the language model to use
        temperature: Temperature setting for the language model
        connection_string: PostgreSQL connection string (defaults to POSTGRES_URI env var)
        table_name: Name of the table to store messages
        system_message: System message to use in the conversations
        language: Language to respond in
        streaming: Whether to enable streaming responses
        
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
    
    # Create LLM
    llm = get_openai_chat_model(model_name=model_name, temperature=temperature)
    
    # Create chat manager with the established connection
    chat_manager = ChatManager(
        llm=llm,
        connection_string=connection_string,
        connection=connection,  # Pass the connection here
        table_name=table_name,
        system_message=system_message
    )
    
    # Define the chain function that will be returned
    def chain_func(message: str) -> Dict[str, Any]:
        if streaming:
            response = chat_manager.stream_chat(thread_id, message, language)
        else:
            response = chat_manager.chat(thread_id, message, language)
            
        return {
            "question": message,
            "answer": response,
            "thread_id": thread_id
        }
    
    # Add helper methods to the function for additional operations
    chain_func.get_history = lambda: chat_manager.get_message_history(thread_id)
    chain_func.add_message = lambda content, is_human=True: chat_manager.add_message(thread_id, content, is_human)
    chain_func.clear_history = lambda: chat_manager.clear_history(thread_id)
    
    # Define the cleanup function to close connection when done
    def cleanup():
        connection.close()
    
    # Add cleanup method to the function
    chain_func.cleanup = cleanup
    
    return chain_func 