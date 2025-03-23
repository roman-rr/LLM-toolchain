from langchain_core.tools import Tool
from langchain_experimental.utilities.python import PythonREPL

def get_calculator_tool():
    """Create a calculator tool using Python REPL"""
    python_repl = PythonREPL()
    
    return Tool(
        name="calculator",
        func=python_repl.run,
        description="Useful for performing calculations using Python. Input should be a Python expression like '2 + 2' or more complex calculations."
    )