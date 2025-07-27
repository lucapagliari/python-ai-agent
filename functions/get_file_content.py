import os
from config import MAX_CHARS

def get_file_content(working_directory, file_path):
    combined_path_abs = os.path.abspath(os.path.join(working_directory, file_path))
    working_dir_abs = os.path.abspath(working_directory)

    if not combined_path_abs.startswith(working_dir_abs):
        return(f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(combined_path_abs):
        return(f'Error: File not found or is not a regular file: "{file_path}"')
    
    try:
        with open(combined_path_abs, "r") as f:
            file_content_string = f.read(MAX_CHARS + 1)
            if len(file_content_string) > MAX_CHARS:
                return f'{file_content_string[:MAX_CHARS]}[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return file_content_string
    except Exception as e:
        return f'Error:{e}'