from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from app.tools import WeatherTool, MathTool, LLMTool
from app.config import Config

def create_tool_selector():
    """Create a simple tool selector that routes queries intelligently using LLM."""
    
    # Initialize tool instances
    weather_tool_instance = WeatherTool()
    math_tool_instance = MathTool()
    llm_tool_instance = LLMTool()
    
    # Create LangChain tools using StructuredTool
    tools = {
        "weather": StructuredTool.from_function(
            func=weather_tool_instance._run,
            name="WeatherTool",
            description="Useful for getting current weather information for a specific city."
        ),
        "math": StructuredTool.from_function(
            func=math_tool_instance._run,
            name="MathTool",
            description="Useful for performing basic math operations."
        ),
        "llm": StructuredTool.from_function(
            func=llm_tool_instance._run,
            name="LLMTool",
            description="Useful for answering general knowledge questions."
        )
    }
    
    # Initialize the LLM for tool selection
    api_key = Config.GROQ_API_KEY
    
    if not api_key or api_key == "your_groq_api_key_here":
        # Return None if no API key - fallback to keyword routing
        return None
    
    try:
        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name=Config.DEFAULT_GROQ_MODEL
        )
        
        # Return a simple executor object
        class SimpleAgentExecutor:
            def __init__(self, llm, tools):
                self.llm = llm
                self.tools = tools
            
            def invoke(self, inputs):
                query = inputs.get("input", "")
                
                # Use LLM to determine which tool to use
                system_prompt = f"""You are a tool selector. Given a user query, determine which tool to use.
Available tools:
- WeatherTool: For weather-related queries (temperature, forecast, weather conditions in cities)
- MathTool: For mathematical calculations (addition, subtraction, multiplication, division)
- LLMTool: For general knowledge questions, explanations, or anything else

Respond with ONLY the tool name (WeatherTool, MathTool, or LLMTool) and nothing else.

User query: {query}"""
                
                # Get tool selection from LLM
                try:
                    response = self.llm.invoke(system_prompt)
                    tool_name = response.content.strip()
                except Exception as e:
                    print(f"Error selecting tool: {e}")
                    tool_name = "LLMTool"
                
                # Map to our tool keys
                tool_map = {
                    "WeatherTool": "weather",
                    "MathTool": "math",
                    "LLMTool": "llm"
                }
                
                selected_tool_key = tool_map.get(tool_name, "llm")
                selected_tool = self.tools[selected_tool_key]
                
                # Execute the tool
                result = selected_tool.func(query)
                
                # Create a mock action object for compatibility
                class MockAction:
                    def __init__(self, tool_name, tool_input):
                        self.tool = tool_name
                        self.tool_input = tool_input
                
                return {
                    "output": result,
                    "intermediate_steps": [(MockAction(tool_name, query), result)]
                }
        
        return SimpleAgentExecutor(llm, tools)
        
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        return None