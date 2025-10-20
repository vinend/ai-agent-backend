import re
from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

class MathTool(BaseTool):
    name: str = "math"
    description: str = "Useful for performing basic math operations like addition, subtraction, multiplication, and division"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool to perform math operations."""
        # Extract the math expression from the query
        # Look for patterns like "what is 42 * 7" or just "42 * 7"
        query_lower = query.lower()
        
        # Common phrases to remove
        phrases_to_remove = [
            "what is ",
            "calculate ",
            "compute ",
            "solve ",
            "math: ",
            "math "
        ]
        
        for phrase in phrases_to_remove:
            query_lower = query_lower.replace(phrase, "")
        
        # Extract numbers and operators using regex
        # This pattern matches basic arithmetic expressions
        pattern = r"([-+]?\d*\.?\d+)\s*([+\-*/x])\s*([-+]?\d*\.?\d+)"
        matches = re.findall(pattern, query_lower)
        
        if matches:
            # Process the first match found
            num1_str, operator, num2_str = matches[0]
            num1 = float(num1_str)
            num2 = float(num2_str)
            
            try:
                if operator in ['*', 'x']:
                    result = num1 * num2
                elif operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '/':
                    if num2 == 0:
                        return "Error: Division by zero"
                    result = num1 / num2
                else:
                    return f"Unknown operator: {operator}"
                
                # Return integer if result is a whole number, otherwise float
                if result.is_integer():
                    return str(int(result))
                else:
                    return str(result)
            except Exception as e:
                return f"Error calculating: {str(e)}"
        else:
            return "Could not parse math expression from query"
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Asynchronous version of the tool."""
        return self._run(query, run_manager=run_manager)