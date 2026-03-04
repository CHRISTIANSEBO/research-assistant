from agent.assistant import create_agent
from agent.file_handler import save_research
from langchain_core.messages import HumanMessage, AIMessage

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
    # Create the agent once
    agent = create_agent()
    
    # Initialize empty chat history list
    chat_history = []
    
    # Show the header when app starts
    print_header()
    
    # Keep the conversation alive with a loop
    while True:
        # Get user input
        query = input("You: ")
        
        # Allow the user to exit cleanly
        if query.lower() == "exit":
            print("\nGoodbye! Happy researching. 👋\n")
            break
        
        # Show a thinking indicator while agent works
        print("\n🔎 Researching...\n")

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

        # Add this exchange to chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=output))

if __name__ == "__main__":
    main()
