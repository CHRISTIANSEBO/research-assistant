import os
from datetime import datetime

def save_research(query, result):
    # Create a 'results' folder if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/research_{timestamp}.txt"
    
    # Write the query and result to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write("AI Research Assistant\n")
        f.write("="*50 + "\n\n")
        f.write(f"Query: {query}\n\n")
        f.write("Result:\n")
        f.write(result + "\n")
    
    return filename