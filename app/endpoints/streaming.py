from flask import Blueprint, request, jsonify
from flask_socketio import emit
import os
import time

streaming_bp = Blueprint('streaming_bp', __name__)

# For the SocketIO events, we'll define them in the main app
# but we'll include a regular endpoint for streaming as well

@streaming_bp.route('/stream', methods=['POST'])
def stream_query():
    """Stream the response for a query using server-sent events."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    user_query = data['query']
    
    def generate():
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
            
            # Stream the response in chunks
            response = {
                'query': user_query,
                'tool_used': tool_used,
                'result': result
            }
            
            # Yield each part of the response
            yield f"data: {jsonify(response).get_json()}\n\n"
            
        except Exception as e:
            error_response = {
                'query': user_query,
                'tool_used': 'error',
                'result': f'Error processing query: {str(e)}'
            }
            yield f"data: {jsonify(error_response).get_json()}\n\n"
    
    return generate(), {'Content-Type': 'text/event-stream'}


# For SocketIO, we'll add the event handlers to the main app
# but we'll define the logic here
def register_socketio_events(socketio):
    @socketio.on('query')
    def handle_query_socket(data):
        """Handle query via WebSocket."""
        user_query = data.get('query', '')
        
        if not user_query:
            emit('error', {'message': 'Query is required'})
            return
        
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
            
            emit('result', response)
            
        except Exception as e:
            error_response = {
                'query': user_query,
                'tool_used': 'error',
                'result': f'Error processing query: {str(e)}'
            }
            emit('error', error_response)