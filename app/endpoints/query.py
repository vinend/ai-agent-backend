from flask import Blueprint, request, jsonify
from app.utils.tool_selector import create_tool_selector
import os
import re

query_bp = Blueprint('query_bp', __name__)

# Initialize the agent once
agent_executor = create_tool_selector()

@query_bp.route('/query', methods=['POST'])
def handle_query():
    """Handle user queries and route them to appropriate tools using LangChain agent."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    user_query = data['query']
    
    try:
        # Try to use the LangChain agent if available
        if agent_executor is not None:
            try:
                result_dict = agent_executor.invoke({"input": user_query})
                
                # Extract the tool used from the agent's intermediate steps
                tool_used = "agent"
                if "intermediate_steps" in result_dict and len(result_dict["intermediate_steps"]) > 0:
                    tool_name = result_dict["intermediate_steps"][0][0].tool
                    tool_used = tool_name.lower().replace("tool", "")
                
                response = {
                    'query': user_query,
                    'tool_used': tool_used,
                    'result': result_dict.get("output", str(result_dict)),
                    'agent_used': True
                }
                
                return jsonify(response)
                
            except Exception as agent_error:
                print(f"Agent error: {str(agent_error)}")
                # Fall back to keyword-based routing
                pass
        
        # Fallback: Simple keyword-based routing
        query_lower = user_query.lower()
        
        if any(keyword in query_lower for keyword in ["weather", "temperature", "rain", "sunny", "cloudy", "hot", "cold"]):
            tool_used = "weather"
            from app.tools.weather_tool import WeatherTool
            result = WeatherTool()._run(user_query)
        elif any(op in query_lower for op in ["+", "-", "*", "x", "/", "multiply", "divide", "add", "subtract", "what is"]):
            # Check if it contains numbers to avoid false positives
            if re.search(r'\d', query_lower):
                tool_used = "math"
                from app.tools.math_tool import MathTool
                result = MathTool()._run(user_query)
            else:
                tool_used = "llm"
                from app.tools.llm_tool import LLMTool
                result = LLMTool()._run(user_query)
        else:
            tool_used = "llm"
            from app.tools.llm_tool import LLMTool
            result = LLMTool()._run(user_query)
        
        response = {
            'query': user_query,
            'tool_used': tool_used,
            'result': result,
            'agent_used': False
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'query': user_query,
            'tool_used': 'error',
            'result': f'Error processing query: {str(e)}',
            'agent_used': False
        }), 500


# Enhanced version that tracks which tool was used
@query_bp.route('/query_enhanced', methods=['POST'])
def handle_query_enhanced():
    """Handle user queries with enhanced tracking - always uses agent if available."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    user_query = data['query']
    
    if agent_executor is None:
        return jsonify({
            'error': 'Agent not available. Please configure GROQ_API_KEY in .env file'
        }), 503
    
    try:
        result_dict = agent_executor.invoke({"input": user_query})
        
        # Extract detailed information from agent execution
        tool_used = "unknown"
        intermediate_steps = []
        
        if "intermediate_steps" in result_dict:
            for step in result_dict["intermediate_steps"]:
                action, observation = step
                tool_used = action.tool.lower().replace("tool", "")
                intermediate_steps.append({
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "observation": str(observation)[:200]  # Truncate for readability
                })
        
        response = {
            'query': user_query,
            'tool_used': tool_used,
            'result': result_dict.get("output", str(result_dict)),
            'agent_used': True,
            'intermediate_steps': intermediate_steps
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'query': user_query,
            'tool_used': 'error',
            'result': f'Error processing query: {str(e)}',
            'agent_used': False
        }), 500