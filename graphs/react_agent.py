from typing import Dict, List, Any, Tuple, Annotated, TypedDict, Sequence, Union, Optional
import operator
import re
from typing_extensions import TypedDict

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage, BaseMessage
)
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langgraph.checkpoint.memory import MemorySaver

from chat_history.base import ChatManager

class AgentState(TypedDict):
    """State for the agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]

def create_agent_executor(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    system_message: str = None,
    checkpointer = None,
):
    """
    Create a REACT agent executor with the given tools and LLM.
    
    Args:
        llm: Language model to use
        tools: List of tools for the agent to use
        system_message: Optional system message to override the default
        checkpointer: Optional checkpointer for memory persistence
        
    Returns:
        Agent executor that can be called with messages
    """
    # Get the standard ReAct prompt
    prompt = hub.pull("hwchase17/react")
    
    # Customize the system message if provided
    if system_message:
        # This is a simplification - you might need to modify the prompt template 
        # more carefully to incorporate the system message
        prompt.template = system_message + "\n\n" + prompt.template
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        return_intermediate_steps=True,  # Important for better formatting
        # Add any other AgentExecutor parameters here
    )
    
    return agent_executor

def create_agent_with_chat_history(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    thread_id: str,
    chat_manager: ChatManager,
    system_message: str = None,
):
    """
    Create a REACT agent that uses the project's chat history system
    
    Args:
        llm: Language model to use
        tools: List of tools for the agent to use
        thread_id: Thread ID for chat history
        chat_manager: Chat manager instance
        system_message: Optional system message
        
    Returns:
        Function to run the agent with chat history
    """
    agent_executor = create_agent_executor(
        llm=llm, 
        tools=tools,
        system_message=system_message,
    )
    
    # Define a function to run the agent with chat history
    def run_agent(message: str):
        # Get existing messages from chat history
        history = chat_manager.get_message_history(thread_id)
        
        # Format chat history as a string for the old-style agent
        chat_history_str = ""
        if history:
            for msg in history:
                prefix = "Human: " if msg["is_human"] else "AI: "
                chat_history_str += prefix + msg["content"] + "\n"
        
        # Add message to chat history
        chat_manager.add_message(thread_id, message, is_human=True)
        
        # Run the agent with the old-style input format
        response = agent_executor.invoke({
            "input": message,
            "chat_history": chat_history_str
        })
        
        # Extract the response
        output = response.get("output", "")
        
        # Add the response to chat history
        chat_manager.add_message(thread_id, output, is_human=False)
        
        return {
            "thread_id": thread_id,
            "question": message,
            "answer": output,
            "full_response": response
        }
    
    # Helper function to format tool outputs with proper line breaks
    def format_tool_output(text):
        # Add newlines after Action: and Action Input: patterns
        text = re.sub(r'(Action: .+?)([A-Z])', r'\1\n\2', text)
        text = re.sub(r'(Action Input: .+?)([A-Z])', r'\1\n\2', text)
        return text
    
    # Define a streaming version using callbacks
    def stream_agent(message: str):
        # Since standard AgentExecutor doesn't natively support token streaming
        # we'll run the full execution and then yield the properly formatted result
        result = run_agent(message)
        
        # Format the answer for better readability
        formatted_answer = format_tool_output(result["answer"])
        
        # Just yield the complete formatted answer
        yield formatted_answer
        
        return result
    
    # Return both regular and streaming functions
    return {
        "run": run_agent,
        "stream": stream_agent
    } 