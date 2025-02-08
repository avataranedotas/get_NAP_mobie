
from datetime import datetime

# Define the file paths
old_path = "old.txt"
watch_path = "watchbusy.txt"
ignore_path = "ignore.txt"
old2_path = "old2.txt"

# Obter os postos que estão no OLD (e OLD2) mas não estão no WATCHBUSY nem no IGNORE

# Open files
with open(old_path, "r") as file1, open(watch_path, "r") as file2, open(ignore_path, "r") as file3, open(old2_path, "r") as file4:
    # Read lines from files
    old_lines = file1.readlines()
    watch_lines = file2.readlines()
    ignore_lines = file3.readlines()
    old2_lines = file4.readlines()
    
    # Find 1
    non1 = set(old_lines) - set(watch_lines)
    non1 = non1 - set(ignore_lines)

    # Find 2
    non2 = set(old2_lines) - set(watch_lines)
    non2 = non2 - set(ignore_lines)


# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if non1:

    # Write the matching lines to a new file or print them
    with open("new_disused.txt", "a") as output_file:
        output_file.write(f"Timestamp: {timestamp}\n")
        output_file.writelines(non1)

if non2:

    # Write the matching lines to a new file or print them
    with open("new_disused2.txt", "a") as output_file:
        output_file.write(f"Timestamp: {timestamp}\n")
        output_file.writelines(non2)
        
