import os
import re

# File paths
declaration_file = "sonia_function_declaration.c"
source_file = "sonia.c"
output_dir = "extracted_functions"

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read function declarations and get function names
with open(declaration_file, 'r') as decl_file:
    function_declarations = decl_file.readlines()

# Function to extract the function name from a declaration line
def get_function_name(declaration_line):
    match = re.search(r'\b\w+\b\s+(\w+)\s*\(.*\)', declaration_line)
    if match:
        return match.group(1)
    return None

# Read source code file
with open(source_file, 'r') as src_file:
    source_code = src_file.read()

# Split source code into blocks using the function markers
function_blocks = re.split(r'(//----- \([0-9A-Fa-f]+\) --------------------------------------------------------)', source_code)

# Extract functions by their declaration name
for line in function_declarations:
    function_name = get_function_name(line)
    
    if function_name:
        # Search each block for the function name and extract it
        for i in range(1, len(function_blocks), 2):  # Only check the even-index blocks (function bodies)
            function_body = function_blocks[i] + function_blocks[i+1]  # Combine the marker and the body
            if re.search(rf'\b{function_name}\b\s*\(', function_body):
                output_path = os.path.join(output_dir, f"{function_name}.txt")
                with open(output_path, 'w') as f:
                    f.write(function_body)
                print(f"Extracted {function_name} to {output_path}")
                break
        else:
            print(f"Function {function_name} not found in {source_file}")
