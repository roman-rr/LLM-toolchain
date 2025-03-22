#!/usr/bin/env python
"""
Command-line interface for interactive chat with persistent history.
"""
import argparse
import os
import sys

from chains.chat_history_chain import create_chain


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Interactive chat with persistent history")
    parser.add_argument("--thread", default="default", help="Thread ID for this conversation")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature setting for the LLM")
    parser.add_argument("--language", default="English", help="Language to respond in")
    parser.add_argument("--system_message", default="You are a helpful assistant.", 
                        help="System message to use in the conversations")
    parser.add_argument("--message", help="Single message to send (for non-interactive mode)")
    parser.add_argument("--streaming", action="store_true", help="Enable streaming responses")
    parser.add_argument("--clear_history", action="store_true", help="Clear the thread history before starting")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Create the chain
        chain = create_chain(
            thread_id=args.thread,
            model_name=args.model,
            temperature=args.temperature,
            system_message=args.system_message,
            language=args.language,
            streaming=args.streaming
        )
        
        # Clear history if requested
        if args.clear_history:
            chain.clear_history()
            print(f"Cleared history for thread: {args.thread}")
        
        # Single message mode
        if args.message:
            response = chain(args.message)
            print(f"Response: {response['answer']}")
            return
        
        # Interactive mode
        print(f"Starting interactive chat (thread: {args.thread}, model: {args.model})")
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
                    history = chain.get_history()
                    if not history:
                        print("No conversation history.")
                    else:
                        print("\nConversation History:")
                        for i, msg in enumerate(history):
                            speaker = "You:" if msg["type"] == "human" else "Assistant:"
                            print(f"{speaker} {msg['content']}")
                    continue
                
                # Check for clear command
                if user_input.lower() == "clear":
                    chain.clear_history()
                    print("Conversation history cleared.")
                    continue
                
                # Send message to the chain
                print("\nAssistant: ", end="", flush=True)
                if not args.streaming:
                    response = chain(user_input)
                    # Print just the answer content
                    print(response["answer"])
                else:
                    # With streaming, we should also ensure we're getting just the content
                    response = chain(user_input)
                    print()  # Add a newline after streaming response
                
            except KeyboardInterrupt:
                print("\nEnding conversation.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 