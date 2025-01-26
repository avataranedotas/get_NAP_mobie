
from datetime import datetime

# Define the file paths
file1_path = "old.txt"
file2_path = "watchbusy.txt"
file3_path = "ignore.txt"

# Obter os postos que estão no OLD mas não estão no WATCHBUSY nem no IGNORE

# Open both files and compare line by line
with open(file1_path, "r") as file1, open(file2_path, "r") as file2, open(file3_path, "r") as file3:
    # Read lines from both files
    file1_lines = file1.readlines()
    file2_lines = file2.readlines()
    file3_lines = file3.readlines()
    
    # Find non-matching lines
    non_matching_lines = set(file1_lines) - set(file2_lines)
    non_matching_lines = non_matching_lines - set(file3_lines)

# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if non_matching_lines:

    # Write the matching lines to a new file or print them
    with open("new_disused.txt", "a") as output_file:
        output_file.write(f"Timestamp: {timestamp}\n")
        output_file.writelines(non_matching_lines)
