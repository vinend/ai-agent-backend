import re
import ast
import operator
from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

class MathTool(BaseTool):
    name: str = "math"
    description: str = "Useful for performing mathematical operations including complex expressions with multiple operations, parentheses, exponents, etc."
    
    def _extract_expression(self, query: str) -> str:
        """Extract mathematical expression from natural language query."""
        query_lower = query.lower()
        
        # Common phrases to remove
        phrases_to_remove = [
            "what is ",
            "what's ",
            "whats ",
            "calculate ",
            "compute ",
            "solve ",
            "evaluate ",
            "math: ",
            "math ",
            "give me ",
            "tell me ",
            "find ",
            "the result ",
            "the answer ",
            "of ",
            "for ",
        ]
        
        for phrase in phrases_to_remove:
            query_lower = query_lower.replace(phrase, "")
        
        # Remove question marks and extra whitespace
        query_lower = query_lower.replace("?", "").strip()
        
        # Replace 'x' with '*' for multiplication (both standalone and adjacent to numbers)
        query_lower = re.sub(r'(\d)\s*x\s*(\d)', r'\1*\2', query_lower)
        query_lower = query_lower.replace(' x ', '*')
        
        # Replace common word operators
        query_lower = query_lower.replace(" plus ", "+")
        query_lower = query_lower.replace(" minus ", "-")
        query_lower = query_lower.replace(" times ", "*")
        query_lower = query_lower.replace(" divided by ", "/")
        query_lower = query_lower.replace(" multiply ", "*")
        query_lower = query_lower.replace(" divide ", "/")
        query_lower = query_lower.replace(" add ", "+")
        query_lower = query_lower.replace(" subtract ", "-")
        
        # Remove any remaining non-mathematical words
        # Keep only digits, operators, parentheses, decimal points, and whitespace
        expression = re.sub(r'[a-zA-Z]+', '', query_lower)
        
        # Clean up extra whitespace
        expression = ' '.join(expression.split())
        
        return expression.strip()
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate a mathematical expression using AST."""
        # Define allowed operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.FloorDiv: operator.floordiv,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }
        
        def eval_node(node):
            if isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Python 3.7 and earlier
                return node.n
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                return operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported operation: {type(node).__name__}")
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')
            # Evaluate the AST
            result = eval_node(tree.body)
            return result
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool to perform math operations."""
        try:
            # Extract the mathematical expression
            expression = self._extract_expression(query)
            
            if not expression:
                return "Could not extract a mathematical expression from the query."
            
            # Remove all whitespace for processing
            expression = expression.replace(" ", "")
            
            # Check if expression contains valid mathematical characters
            if not re.search(r'\d', expression):
                return "No valid mathematical expression found in the query."
            
            # Replace '^' with '**' for exponentiation
            expression = expression.replace('^', '**')
            
            # Validate that expression only contains allowed characters
            allowed_chars = set('0123456789+-*/().** ')
            if not all(c in allowed_chars for c in expression):
                return f"Error: Invalid characters in expression. Only numbers and operators (+, -, *, /, ^, parentheses) are allowed."
            
            # Evaluate the expression safely
            result = self._safe_eval(expression)
            
            # Format the result
            if isinstance(result, float):
                # Return integer if result is a whole number
                if result.is_infinite():
                    return "Error: Result is infinite"
                elif result != result:  # Check for NaN
                    return "Error: Result is not a number"
                elif result.is_integer():
                    return str(int(result))
                else:
                    # Round to reasonable precision
                    return str(round(result, 10))
            else:
                return str(result)
                
        except ZeroDivisionError:
            return "Error: Division by zero"
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Asynchronous version of the tool."""
        return self._run(query, run_manager=run_manager)