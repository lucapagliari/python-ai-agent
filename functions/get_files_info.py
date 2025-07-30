import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    combined_path_abs = os.path.abspath(os.path.join(working_directory, directory))
    working_dir_abs = os.path.abspath(working_directory)

    if not combined_path_abs.startswith(working_dir_abs):
        return(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    if not os.path.isdir(combined_path_abs):
        return(f'Error: "{directory}" is not a directory')
        
    list_dir = os.listdir(combined_path_abs)
    result_list = []
    for item in list_dir:
        item_path = f'{combined_path_abs}/{item}'
        result_list.append(
            f'- {item}: ' +
            f'file_size={os.path.getsize(item_path)} bytes, ' +
            f'is_dir={os.path.isdir(item_path)}'
        )
    return f'{'\n'.join(result_list)}'
