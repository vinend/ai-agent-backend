from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain_groq import ChatGroq
from app.tools import WeatherTool, MathTool, LLMTool
from app.config import Config

def create_tool_selector():
    """Create a LangChain agent that can select and use appropriate tools."""
    
    # Initialize tools
    tools = [
        Tool(
            name="WeatherTool",
            func=WeatherTool()._run,
            description="Useful for getting weather information for a specific city"
        ),
        Tool(
            name="MathTool",
            func=MathTool()._run,
            description="Useful for performing basic math operations like addition, subtraction, multiplication, and division"
        ),
        Tool(
            name="LLMTool",
            func=LLMTool()._run,
            description="Useful for answering general questions that don't fit other tools"
        )
    ]
    
    # Initialize the LLM for the agent
    api_key = Config.GROQ_API_KEY
    
    if not api_key or api_key == "your_groq_api_key_here":
        # If no API key, we'll use a mock response
        llm = None  # This would need to be handled differently in a real implementation
    else:
        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name=Config.DEFAULT_GROQ_MODEL
        )
    
    # Create the agent
    # For now, we'll use the simpler keyword-based routing in the endpoint
    # The full agent implementation would require more complex setup
    return None  # Placeholder - we'll use keyword-based routing for now