from typing import Dict, List, Any, Tuple, Annotated, TypedDict, Sequence, Union, Optional
import operator
from typing_extensions import TypedDict
import json

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage, BaseMessage
)
from langchain_core.tools import BaseTool

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from chat_history.base import ChatManager

def create_conversational_agent(
    llm: BaseLanguageModel,
    tools: List[BaseTool] = None,
    system_message: str = None,
):
    """
    Create a conversational agent that can use tools but prioritizes natural conversation.
    
    Args:
        llm: Language model to use
        tools: Optional list of tools for the agent to use
        system_message: Optional system message
        
    Returns:
        Graph for the conversational agent
    """
    tools_for_execution = tools.copy() if tools else []  # Keep a copy for execution
    
    if tools:
        # Bind tools to the model if supported
        if hasattr(llm, "bind_tools"):
            llm_with_tools = llm.bind_tools(tools)
        else:
            # For models that don't support .bind_tools directly
            from langchain.agents.format_scratchpad import format_to_openai_functions
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
            
            # Format tools as OpenAI functions
            functions = [tool.metadata for tool in tools]
            llm_with_tools = llm.bind_functions(functions)
    else:
        llm_with_tools = llm
    
    if system_message is None:
        if tools:
            system_message = (
                "You are a helpful, friendly AI assistant that can both have natural conversations "
                "and use tools when necessary to provide accurate and up-to-date information. "
                "Prioritize giving direct answers to user questions. Only use tools when required."
            )
        else:
            system_message = (
                "You are a helpful, friendly AI assistant. Respond in a conversational, helpful manner."
            )
    
    # Define the agent state
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        
    # Define the nodes in our graph
    def agent(state: AgentState) -> dict:
        """Process messages and generate a response"""
        messages = state["messages"]
        
        # Add system message at the beginning if not already there
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=system_message)] + messages
        
        # DEBUGGING
        print(f"Executing agent with {len(messages)} messages")
        print(f"Available tools: {[t.name for t in tools_for_execution]}")
        
        try:
            # Generate model response
            response = llm_with_tools.invoke(messages)
            
            # DEBUGGING
            print(f"Got response: {response.content[:100]}...")
            print(f"Additional kwargs: {response.additional_kwargs if hasattr(response, 'additional_kwargs') else 'None'}")
            
            # Check for tool calls - handling both single function_call and new tool_calls format
            tool_call_detected = False
            tool_name = None
            tool_args = None
            tool_call_id = None
            
            # Check for OpenAI's new tool_calls format
            if hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
                tool_calls = response.additional_kwargs["tool_calls"]
                if tool_calls and len(tool_calls) > 0:
                    tool_call_detected = True
                    tool_call = tool_calls[0]  # Take the first tool call
                    tool_name = tool_call["function"]["name"]
                    tool_call_id = tool_call["id"]  # Save the tool_call_id
                    try:
                        tool_args_str = tool_call["function"]["arguments"]
                        # Handle different argument formats
                        if "__arg1" in tool_args_str:
                            # Handle arguments like {"__arg1":"Paris weather forecast next week"}
                            parsed_args = json.loads(tool_args_str)
                            tool_args = {"query": parsed_args.get("__arg1", "")}
                        else:
                            tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError:
                        print(f"Error decoding tool arguments: {tool_call['function']['arguments']}")
                        return {"messages": [AIMessage(content="I encountered an error processing the request.")]}
            
            # Also check for older function_call format as fallback
            elif hasattr(response, "additional_kwargs") and "function_call" in response.additional_kwargs:
                tool_call_detected = True
                function_call = response.additional_kwargs["function_call"]
                tool_name = function_call["name"]
                try:
                    tool_args = json.loads(function_call["arguments"])
                except json.JSONDecodeError:
                    print(f"Error decoding tool arguments: {function_call['arguments']}")
                    return {"messages": [AIMessage(content="I encountered an error processing the request.")]}
            
            # Process tool call if detected
            if tool_call_detected and tool_name:
                print(f"Tool call detected: {tool_name}")
                
                # Find the matching tool
                matching_tools = [t for t in tools_for_execution if t.name == tool_name]
                if matching_tools:
                    tool = matching_tools[0]
                    print(f"Found matching tool: {tool.name}")
                    
                    # Execute the tool
                    tool_input = tool_args.get("query", "") if isinstance(tool_args, dict) else str(tool_args)
                    print(f"Executing tool with input: {tool_input}")
                    
                    try:
                        tool_result = tool.invoke(tool_input)
                        print(f"Tool result: {tool_result}")
                        
                        # Create a proper tool response message
                        # Import directly, don't rely on globals()
                        from langchain_core.messages import ToolMessage
                        
                        # Create the tool message with correct tool_call_id
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call_id,
                            name=tool_name
                        )
                        
                        # Add tool result to messages and generate final response
                        final_messages = messages + [response, tool_message]
                        print("Generating final response with tool result")
                        final_response = llm_with_tools.invoke(final_messages)
                        
                        print(f"Final response after tool use: {final_response.content[:100]}...")
                        # Return the final response after tool use
                        return {"messages": [final_response]}
                    except Exception as e:
                        print(f"Error executing tool: {e}")
                        return {"messages": [AIMessage(content=f"I tried to use {tool_name} to answer your question, but encountered an error: {str(e)}")]}
                else:
                    print(f"ERROR: Tool {tool_name} not found in available tools: {[t.name for t in tools_for_execution]}")
                    return {"messages": [AIMessage(content=f"I tried to use {tool_name} to answer your question, but I don't have access to that tool.")]}
            
            # Return updated state with AI response
            return {"messages": [response]}
        except Exception as e:
            import traceback
            print(f"ERROR in agent execution: {e}")
            print(traceback.format_exc())
            return {"messages": [AIMessage(content=f"I encountered an error while processing your request: {str(e)}")]}
    
    # Build the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent)
    
    # Set the entry point
    workflow.set_entry_point("agent")
    
    # Build the application
    app = workflow.compile()
    return app

def create_conversational_agent_with_chat_history(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    thread_id: str,
    chat_manager: ChatManager,
    system_message: str = None,
):
    """
    Create a conversational agent that uses the project's chat history system
    
    Args:
        llm: Language model to use
        tools: List of tools for the agent to use
        thread_id: Thread ID for chat history
        chat_manager: Chat manager instance
        system_message: Optional system message
        
    Returns:
        Function to run the agent with chat history
    """
    memory = MemorySaver()
    agent_app = create_conversational_agent(
        llm=llm, 
        tools=tools,
        system_message=system_message,
    )
    
    # Define a function to run the agent with chat history
    def run_agent(message: str):
        # Get existing messages from chat history
        history = chat_manager.get_message_history(thread_id)
        
        # Create messages input
        messages = []
        if history:
            # Convert chat history to the format expected by the agent
            for msg in history:
                if msg["is_human"]:
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add the new user message
        messages.append(HumanMessage(content=message))
        
        # Add message to chat history
        chat_manager.add_message(thread_id, message, is_human=True)
        
        # Run the agent
        config = {"configurable": {"thread_id": thread_id}}
        response = agent_app.invoke({"messages": messages}, config)
        
        # Extract the AI message
        ai_message = response["messages"][-1]
        
        # Add the response to chat history
        chat_manager.add_message(thread_id, ai_message.content, is_human=False)
        
        return {
            "thread_id": thread_id,
            "question": message,
            "answer": ai_message.content,
        }
    
    # Define a streaming version
    def stream_agent(message: str):
        # Get existing messages from chat history
        history = chat_manager.get_message_history(thread_id)
        
        # Create messages input
        messages = []
        if history:
            # Convert chat history to the format expected by the agent
            for msg in history:
                if msg["is_human"]:
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add the new user message
        messages.append(HumanMessage(content=message))
        
        # Add message to chat history
        chat_manager.add_message(thread_id, message, is_human=True)
        
        # Stream the agent
        config = {"configurable": {"thread_id": thread_id}}
        
        # Store the complete AI response
        full_response = ""
        
        for chunk in agent_app.stream(
            {"messages": messages},
            config,
        ):
            if chunk.get("messages"):
                ai_message = chunk["messages"][-1]
                if hasattr(ai_message, "content") and ai_message.content:
                    text = ai_message.content
                    full_response = text
                    yield text
        
        # Add to chat history when complete
        chat_manager.add_message(thread_id, full_response, is_human=False)
        
        return {
            "thread_id": thread_id,
            "question": message,
            "answer": full_response
        }
    
    # Return both regular and streaming functions
    return {
        "run": run_agent,
        "stream": stream_agent
    }