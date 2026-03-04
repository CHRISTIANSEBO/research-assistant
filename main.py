from agent.assistant import create_agent

def main():
    # Create the agent
    agent = create_agent()
    
    # Ask the user what they want to research
    query = input("What would you like to research? ")
    
    # Pass the query to the agent and get a response
    response = agent.invoke({"input": query})
    
    # Print the final answer
    print("\n--- Research Result ---")
    print(response["output"])

# Only run main() if this file is executed directly
if __name__ == "__main__":
    main()
    