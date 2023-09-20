import re
import sys

seq_hash = {}
all_lines = []
count = 0

with open(sys.argv[1], 'r') as file:
    for line in file:
        line = line.strip()

        if re.match(r'>', line):
            if count + 1 < len(all_lines):  # Check if count is a valid index
                count += 1
                all_lines.append(line)
                count += 1
            else:
                all_lines.append(line)
                count += 1
        else:
            if count < len(all_lines):  # Check if count is a valid index
                if all_lines[count]:
                    all_lines[count] += line
                else:
                    all_lines[count] = line
            else:
                all_lines.append(line)  # Add a new line to the list

for i in range(0, len(all_lines), 2):
    header = all_lines[i]
    seq = all_lines[i + 1]
    
    if len(seq) >= 100:
        seq_hash[seq] = header

for key, value in seq_hash.items():
    print(value)
    print(key)

