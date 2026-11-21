import os
from datetime import datetime

def save_research(query, result):
    # Create a 'results' folder if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Generate a filename using the current timestamp. Second-granularity
    # timestamps can collide when two researches finish in the same second,
    # so if the file already exists we append a numeric suffix to avoid
    # silently overwriting an earlier result.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/research_{timestamp}.txt"
    if os.path.exists(filename):
        suffix = 1
        while os.path.exists(f"results/research_{timestamp}_{suffix}.txt"):
            suffix += 1
        filename = f"results/research_{timestamp}_{suffix}.txt"
    
    # Write the query and result to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write("AI Research Assistant\n")
        f.write("="*50 + "\n\n")
        f.write(f"Query: {query}\n\n")
        f.write("Result:\n")
        f.write(result + "\n")
    
    return filename