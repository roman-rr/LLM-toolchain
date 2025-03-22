from typing import Dict, List, Any, Optional
import os
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from .memory import get_message_history, create_memory
from .handlers import get_streaming_llm

class ChatManager:
    """Manages chat conversations with thread-based history using PostgreSQL."""
    
    def __init__(self, 
                 llm=None, 
                 connection_string=None,
                 connection=None,
                 table_name="message_store",
                 system_message="You are a helpful assistant."):
        """
        Initialize the chat manager.
        
        Args:
            llm: The language model to use (defaults to ChatOpenAI)
            connection_string: PostgreSQL connection string
            connection: Existing PostgreSQL connection to use
            table_name: The table name to store messages
            system_message: The system message to use in conversations
        """
        # Set default LLM if not provided
        self.llm = llm or ChatOpenAI(temperature=0.7)
        
        # Store connection or connection string
        self.connection = connection
        self.connection_string = connection_string or os.getenv(
            "POSTGRES_URI", 
            "postgresql://username:password@localhost:5432/yourdb"
        )
        
        self.table_name = table_name
        self.system_message = system_message
        
        # Ensure the message store table exists
        if self.connection:
            self._init_table(self.connection)
        else:
            # Create a temporary connection if none provided
            import psycopg
            temp_connection = psycopg.connect(self.connection_string)
            self._init_table(temp_connection)
            temp_connection.close()
    
    def _init_table(self, connection):
        """Initialize the database table if it doesn't exist."""
        # Use the create_tables static method to initialize the table
        PostgresChatMessageHistory.create_tables(connection, self.table_name)
    
    def _create_conversation_chain(self, thread_id: str, language: str = "English"):
        """Create a conversation chain with the appropriate memory and prompt."""
        # Create message history for this thread
        message_history = get_message_history(
            thread_id,                 
            self.table_name,          
            connection=self.connection  
        )
        
        # Create prompt template with language support
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{self.system_message} Respond in the {language} language."),
            ("placeholder", "{history}"),
            ("human", "{input}")
        ])
        
        # Create a simple chain using the newer approach
        chain = prompt | self.llm
        
        # Add message history to the chain
        conversation_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: message_history,  # Function that returns message history for a session
            input_messages_key="input",  # The key for user inputs (should match prompt)
            history_messages_key="history"  # The key for message history in the prompt
        )
        
        return conversation_with_history
    
    def get_message_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific thread."""
        history = get_message_history(
            thread_id=thread_id,
            table_name=self.table_name,
            connection=self.connection
        )
        messages = history.messages
        
        # Convert to a more user-friendly format
        result = []
        for msg in messages:
            result.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()  # PostgreSQL doesn't store timestamps by default
            })
        
        return result
    
    def add_message(self, thread_id: str, content: str, is_human: bool = True) -> None:
        """Manually add a message to the thread history."""
        history = get_message_history(
            thread_id=thread_id,
            table_name=self.table_name,
            connection=self.connection
        )
        if is_human:
            history.add_user_message(content)
        else:
            history.add_ai_message(content)
    
    def clear_history(self, thread_id: str) -> None:
        """Clear the message history for a specific thread."""
        history = get_message_history(
            thread_id=thread_id,
            table_name=self.table_name,
            connection=self.connection
        )
        history.clear()
    
    def chat(self, thread_id: str, message: str, language: str = "English") -> str:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            thread_id: The unique identifier for this conversation thread
            message: The user's message
            language: The language to respond in
        
        Returns:
            The AI's response
        """
        conversation = self._create_conversation_chain(thread_id, language)
        response = conversation.invoke(
            {"input": message},
            {"configurable": {"session_id": thread_id}}
        )
        
        # Extract just the content from the AIMessage response
        if hasattr(response, 'content'):
            # If response is an AIMessage object
            return response.content
        elif isinstance(response, dict) and "output" in response:
            # If response is a dictionary with an output key
            return response["output"]
        elif isinstance(response, str):
            # If response is already a string
            return response
        else:
            # For any other case, convert to string
            return str(response)
    
    def stream_chat(self, thread_id: str, message: str, language: str = "English"):
        """
        Stream a response for a given message.
        
        Args:
            thread_id: The unique identifier for this conversation thread
            message: The user's message
            language: The language to respond in
            
        Returns:
            The complete AI response text after streaming is complete
        """
        # Create a streaming-enabled version of the LLM
        streaming_llm = get_streaming_llm(self.llm)
        
        # Get message history
        message_history = get_message_history(
            thread_id=thread_id,
            table_name=self.table_name,
            connection=self.connection
        )
        
        # Create prompt template with language support
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{self.system_message} Respond in the {language} language."),
            ("placeholder", "{history}"),
            ("human", "{input}")
        ])
        
        # Create a conversation chain with streaming capability
        conversation = RunnableWithMessageHistory(
            prompt | streaming_llm,
            lambda session_id: message_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
        # Stream the response
        full_content = ""
        for chunk in conversation.stream(
            {"input": message},
            {"configurable": {"session_id": thread_id}}
        ):
            # Extract content from the chunk
            chunk_content = ""
            if hasattr(chunk, 'content'):
                chunk_content = chunk.content
            elif isinstance(chunk, dict) and "output" in chunk:
                chunk_content = chunk["output"]
            elif isinstance(chunk, str):
                chunk_content = chunk
            else:
                chunk_content = str(chunk)
            
            # Print the chunk content without a newline
            print(chunk_content, end="", flush=True)
            
            # Accumulate the full content
            full_content += chunk_content
        
        # Return the complete response content for saving to history
        return full_content 