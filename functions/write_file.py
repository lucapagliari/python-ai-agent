import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to write the file to, relative to the working directory. If not provided, writes to the working directory itself.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            )
        },
    ),
)

def write_file(working_directory, file_path, content):
    combined_path_abs = os.path.abspath(os.path.join(working_directory, file_path))
    working_dir_abs = os.path.abspath(working_directory)

    if not combined_path_abs.startswith(working_dir_abs):
        return(f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory')
    
    try:
        dir_name = os.path.dirname(combined_path_abs)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(combined_path_abs, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error:{e}'