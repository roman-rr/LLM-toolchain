#!/usr/bin/env python
"""
Command-line interface for interacting with agent chains with persistent history.
"""
import argparse
import os
import sys
import uuid
from typing import List, Optional

from chains.agent_chain import create_chain
from agents.tools.base import get_tools

def list_available_tools():
    """Get a list of all available tool names for display in help"""
    # This is a placeholder - in reality we'd dynamically get this from your tools module
    return ["weather", "search", "calculator"]

def main():
    # Create argument parser with description
    parser = argparse.ArgumentParser(
        description="Interactive agent with tools and persistent history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start an interactive session with a REACT agent
  python -m cli.agent_query --agent_type react --tools weather,search
  
  # Use a conversational agent with a specific system message
  python -m cli.agent_query --agent_type conversational --system_message "You are a helpful travel assistant"
  
  # Execute a single query with streaming enabled
  python -m cli.agent_query --message "What's the weather in New York?" --streaming
  
  # Continue a previous conversation thread
  python -m cli.agent_query --thread 123e4567-e89b-12d3-a456-426614174000
        """
    )
    
    # Basic arguments
    parser.add_argument("--thread", help="Thread ID for this conversation (UUID)")
    parser.add_argument("--agent_type", choices=["react", "conversational"], default="react",
                       help="Type of agent to create (default: react)")
    parser.add_argument("--model", default="gpt-3.5-turbo", 
                       help="LLM model to use (default: gpt-3.5-turbo)")
    parser.add_argument("--temperature", type=float, default=0.7, 
                       help="Temperature setting for the LLM (default: 0.7)")
    
    # Tool arguments
    available_tools = list_available_tools()
    parser.add_argument("--tools", 
                       help=f"Comma-separated list of tools to use. Available: {', '.join(available_tools)}")
    
    # Message and display options
    parser.add_argument("--system_message", 
                       help="System message to use for the agent")
    parser.add_argument("--message", 
                       help="Single message to send (for non-interactive mode)")
    parser.add_argument("--streaming", action="store_true", 
                       help="Enable streaming responses")
    parser.add_argument("--clear_history", action="store_true", 
                       help="Clear the thread history before starting")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process tools list
    tool_list = None
    if args.tools:
        tool_list = [t.strip() for t in args.tools.split(",")]
        # Validate tools
        invalid_tools = [t for t in tool_list if t not in available_tools]
        if invalid_tools:
            parser.error(f"Invalid tools: {', '.join(invalid_tools)}. Available tools: {', '.join(available_tools)}")
    
    try:
        # Create the chain
        agent_chain = create_chain(
            thread_id=args.thread,
            agent_type=args.agent_type,
            model_name=args.model,
            temperature=args.temperature,
            tools=tool_list,
            system_message=args.system_message,
            streaming=args.streaming
        )
        
        # Clear history if requested
        if args.clear_history:
            agent_chain.clear_history()
            print(f"Cleared history for thread: {agent_chain.thread_id}")
        
        # Single message mode
        if args.message:
            print(f"Question: {args.message}")
            
            if args.streaming:
                print("Answer: ", end="", flush=True)
                response_stream = agent_chain(args.message, use_streaming=True)
                
                # For streaming, collect the full response for potential further use
                full_response = ""
                for chunk in response_stream:
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()  # Add newline after streaming response
            else:
                response = agent_chain(args.message)
                print(f"Answer: {response['answer']}")
            
            print(f"Thread ID: {agent_chain.thread_id}")
            return
        
        # Interactive mode
        print(f"Starting interactive chat with {args.agent_type.upper()} agent")
        print(f"Thread ID: {agent_chain.thread_id}")
        print(f"Model: {args.model}")
        print(f"Tools: {tool_list or 'None'}")
        print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.")
        print("Type 'history' to show conversation history.")
        print("Type 'clear' to clear the conversation history.")
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ")
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit"]:
                    print("Ending conversation.")
                    break
                
                # Check for history command
                if user_input.lower() == "history":
                    history = agent_chain.get_history()
                    if not history:
                        print("No conversation history.")
                    else:
                        print("\nConversation History:")
                        for msg in history:
                            speaker = "You:" if msg["is_human"] else "Assistant:"
                            print(f"{speaker} {msg['content']}")
                    continue
                
                # Check for clear command
                if user_input.lower() == "clear":
                    agent_chain.clear_history()
                    print("Conversation history cleared.")
                    continue
                
                # Send message to the chain
                print("\nAssistant: ", end="", flush=True)
                
                if args.streaming:
                    # Use streaming
                    response_stream = agent_chain(user_input, use_streaming=True)
                    
                    # This is a generator that yields chunks of the response
                    for chunk in response_stream:
                        print(chunk, end="", flush=True)
                    print()  # Add a newline after streaming response
                else:
                    # Without streaming
                    response = agent_chain(user_input)
                    print(response["answer"])
                
            except KeyboardInterrupt:
                print("\nEnding conversation.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        # Clean up resources
        agent_chain.cleanup()
    
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 