from flask import Blueprint, request, jsonify
import os
import re

query_bp = Blueprint('query_bp', __name__)

@query_bp.route('/query', methods=['POST'])
def handle_query():
    """Handle user queries and route them to appropriate tools."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    user_query = data['query']
    
    try:
        # Simple keyword-based routing
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
            'result': result
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'query': user_query,
            'tool_used': 'error',
            'result': f'Error processing query: {str(e)}'
        }), 500


# Enhanced version that tracks which tool was used
@query_bp.route('/query_enhanced', methods=['POST'])
def handle_query_enhanced():
    """Handle user queries and route them to appropriate tools with tool tracking."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    user_query = data['query']
    
    try:
        # Simple keyword-based routing for now
        query_lower = user_query.lower()
        
        if any(keyword in query_lower for keyword in ["weather", "temperature", "rain", "sunny", "cloudy", "hot", "cold"]):
            tool_used = "weather"
            from app.tools.weather_tool import WeatherTool
            result = WeatherTool()._run(user_query)
        elif any(op in query_lower for op in ["+", "-", "*", "x", "/", "multiply", "divide", "add", "subtract", "what is"]):
            # Check if it contains numbers to avoid false positives
            import re
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
            'result': result
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'query': user_query,
            'tool_used': 'error',
            'result': f'Error processing query: {str(e)}'
        }), 500