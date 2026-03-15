from agent.assistant import create_research_agent
from agent.file_handler import save_research
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import sys
import argparse

def parse_arguments():
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="AI Research Assistant — powered by Claude and Tavily"
    )
    
    # Add the --topic flag
    parser.add_argument(
        "--topic",
        type=str,
        help="Research topic to start with immediately"
    )
    
    return parser.parse_args()

# Load environment variables from .env at the very start
load_dotenv()

def validate_keys():
    # Check if both API keys are present before starting
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    missing = []
    
    if not anthropic_key:
        missing.append("ANTHROPIC_API_KEY")
    if not tavily_key:
        missing.append("TAVILY_API_KEY")
    
    # If any keys are missing, tell the user exactly what's wrong and exit
    if missing:
        print("\n❌ Missing API keys in your .env file:")
        for key in missing:
            print(f"   - {key}")
        print("\nAdd them to your .env file and try again.\n")
        sys.exit(1)  # Exit the program cleanly with an error code

def print_header():
    # Print a clean header when the app starts
    print("\n" + "="*50)
    print("        🔍 AI Research Assistant")
    print("="*50)
    print("Type your research question to get started.")
    print("Type 'exit' to quit.")
    print("="*50 + "\n")

def print_result(output):
    # Print the result in a clean formatted block
    print("\n" + "-"*50)
    print("📋 RESEARCH RESULT")
    print("-"*50)
    print(output)
    print("-"*50 + "\n")

def main():
     # Validate keys before doing anything else
    validate_keys()

    # Parse command line arguments
    args = parse_arguments()

    # Create the agent once
    agent = create_research_agent()
    
    # Initialize empty chat history list
    chat_history = []
    
    # Show the header when app starts
    print_header()
    
    # If a topic was passed in, use it as the first query
    first_query = args.topic if args.topic else None

    while True:
        # Use the --topic argument for the first query if provided
        if first_query:
            query = first_query
            print(f"You: {query}\n")
            first_query = None  # Clear it so subsequent queries use input()
        else:
            query = input("You: ")

        # Allow the user to exit cleanly
        if query.lower() == "exit":
            print("\nGoodbye! Happy researching. 👋\n")
            break

        # Handle empty input
        if not query.strip():
            print("⚠️ Please enter a research question.\n")
            continue

        # Show a thinking indicator while agent works
        print("\n🔎 Researching...\n")

        try:
            # Pass the query AND the chat history to the agent
            response = agent.invoke({
                "input": query,
                "chat_history": chat_history
            })

            # Extract the output text cleanly
            output = response["output"]

            # Handle both string and list response formats
            if isinstance(output, list):
                output = output[0].get("text", "")

            # Print the formatted result
            print_result(output)

            # Save the result to a file
            filename = save_research(query, output)
            print(f"💾 Research saved to: {filename}\n")

        except Exception as e:
            # Catch any API or runtime error and show a helpful message
            print(f"\n❌ Something went wrong: {str(e)}")
            print("Please try again or check your API keys.\n")

        # Add this exchange to chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=output))

if __name__ == "__main__":
    main()
