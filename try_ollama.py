import os
import ollama
from tqdm import tqdm
import pickle
import dbm

# Directory containing the extracted functions
functions_dir = 'extracted_functions'

idc_script_file = open("ida_script.idc", "w")

# The prompt format for the Llama 3.1 model
prompt_template = (
    "Given the following HLIL decompiled code snippet, provide a Python-style function name "
    "that describes what the code is doing. The name must meet the following criteria: "
    "all lowercase letters, usable in Python code, with underscores between words. "
    "Only return the function name and no other explanation or text data included."
    "I strictly need no bullshit, be sharp and straightforward"
)


def cache_decorator(function):
    def wrapper(*args, **kwargs):
        with dbm.open("ollama_cache","c") as db:
            serialized_args = pickle.dumps((args, kwargs))
            if serialized_args in db:
                return pickle.loads(db[serialized_args])
            result = function(*args, **kwargs)
            db[serialized_args] = pickle.dumps(result)
        return result
    return wrapper

@cache_decorator
def get_function_name(code_snippet, model="llama3.1"):
    # Create the full prompt
    prompt = f"{prompt_template}\n\n{code_snippet}"

    # Send the prompt to the Llama 3.1 model using Ollama
    response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content'].strip()


def get_function_files(functions_dir):
    res = []
    for filename in os.listdir(functions_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(functions_dir, filename)
            if filename.startswith("sub_"):
                res.append((filename,file_path))
    return res


def parse_function_names(functions_dir):
    for filename,file_path in tqdm(get_function_files(functions_dir)):

        with open(file_path, 'r') as f:
            code_snippet = f.read()

        addr = filename.split('_')[1].split('.')[0]
        addr = f"0x{addr}"  # Convert to hexadecimal

        # Get the function name from the model
        function_name = get_function_name(code_snippet, "llama3.1")

        if len(function_name.split()) > 20:
            description = function_name
            description = description.replace("\n", "\\n")
            description = description.replace("'",'"')

            # Create IDC script 

            print(f'set_func_cmt({addr}, "{description}", 0);\n')
            idc_script_file.write(f'set_func_cmt({addr}, "{description}", 0);\n')
        else:
            print(f'MakeName({addr}, "{function_name}");\n')
            idc_script_file.write(f'MakeName({addr}, "{function_name}");\n')

parse_function_names(functions_dir)
