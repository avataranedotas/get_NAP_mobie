
from datetime import datetime

# Define the file paths
file1_path = "inuse_stations.txt"
file2_path = "watchbusy.txt"

# Open both files and compare line by line
with open(file1_path, "r") as file1, open(file2_path, "r") as file2:
    # Read lines from both files
    file1_lines = file1.readlines()
    file2_lines = file2.readlines()
    
    # Find matching lines
    matching_lines = set(file1_lines) & set(file2_lines)


# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Write the matching lines to a new file or print them
with open("charging.txt", "a") as output_file:
    output_file.write(f"Timestamp: {timestamp}\n")
    #output_file.write("Matching Lines:\n")
    output_file.writelines(matching_lines)

print("Matching lines have been written to 'charging.txt'.")

