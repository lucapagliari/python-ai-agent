import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file

def main():
    load_dotenv()
    
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("Usage: python main.py \"your prompt here\" [--verbose]")
        sys.exit(1)

    user_prompt = " ".join(args)
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Write or overwrite files
    - Execute Python files whith optional arguments

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file
        ]
    )

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]),]
    
    MAX_LOOP = 20
    iteration = 0

    while iteration < MAX_LOOP:
        try:
            response = client.models.generate_content(
            model='gemini-2.0-flash-001', 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
                ),
            )

            for candidate in response.candidates:
                messages.append(candidate.content)

            if verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            
            has_function_calls = False
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        has_function_calls = True
                        function_call_result = call_function(part.function_call, verbose)
                        actual_result = function_call_result.parts[0].function_response.response

                        if not actual_result:
                            raise Exception ('Fatal Error during function call')
                        
                        if verbose:
                            print(f"-> {actual_result}")
                        
                        tool_message = types.Content(
                            role="model", 
                            parts=[types.Part(text=str(actual_result))]
                        )
                        messages.append(tool_message)
                    
            if not has_function_calls:
                if response.text:
                    print(response.text)
                    break
            iteration +=1

        except Exception as e:
            print(f'Error encountered: {e}')
            break  


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = function_call_part.args
    function_args["working_directory"]="./calculator"
    function_result = ""

    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f"- Calling function: {function_name}")

    function_dict = {
        'get_file_content': get_file_content,
        'get_files_info': get_files_info,
        'run_python_file': run_python_file,
        'write_file': write_file,
    }
    if function_name in function_dict:
        function_result = function_dict[function_name](**function_args)
    else:
        return types.Content(
            role="tool",
            parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )
        

if __name__ == "__main__":
    main()