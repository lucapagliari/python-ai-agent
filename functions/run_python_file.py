import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
    combined_path_abs = os.path.abspath(os.path.join(working_directory, file_path))
    working_dir_abs = os.path.abspath(working_directory)

    if not combined_path_abs.startswith(working_dir_abs):
        return(f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(combined_path_abs):
        return(f'Error: File "{file_path}" not found')
    if not combined_path_abs.endswith('.py'):
        return(f'Error: "{file_path}" is not a Python file.')
    
    try:
        cmd=[]
        cmd.append('python')
        cmd.append(f'{combined_path_abs}')
        process = subprocess.run(cmd + args, timeout=30, capture_output=True, cwd=working_dir_abs)
        if process.returncode != 0:
            return f'Process exited with code {process.returncode}'
        output = process.stdout.decode('utf-8').strip()
        error = process.stderr.decode('utf-8').strip()
        if len(output) == 0 and len(error) == 0:
            return f'No output produced{error}'
        return f'STDOUT: {output}\nSTDERR: {error}'
    except Exception as e:
        return f'Error: executing Python file: {e}'
