import os
from google.adk.tools import FunctionTool

def read_file_content(file_path: str) -> str:
    """
    (CUSTOM TOOL) Reads and returns the content of a local file
    if it exists. Otherwise, returns an error message.
    
    Args:
        file_path: The path to the local file (e.g., 'content_brief.md').

    Returns:
        The content of the file or an error message.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            # Note: We return the error as a string so the LLM can see it
            return f"Error reading file: {e}"
    else:
        return f"Error: File not found at '{file_path}'."

def write_file_content(file_path: str, content: str) -> str:
    """
    (CUSTOM TOOL) Writes the given content to a local file,
    overwriting it if it exists.
    
    Args:
        file_path: The path to the local file (e.g., 'content_brief.md').
        content: The text content to write to the file.

    Returns:
        A confirmation message on success, or an error message.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote content to '{file_path}'."
    except Exception as e:
        return f"Error writing to file: {e}"

# FIX: Use 'func' and rely on the docstrings for descriptions
file_reader_tool = FunctionTool(
    func=read_file_content
)

file_writer_tool = FunctionTool(
    func=write_file_content
)
