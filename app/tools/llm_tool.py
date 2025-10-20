from langchain.tools import BaseTool
from pydantic import Field
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from groq import Groq
from app.config import Config

class LLMTool(BaseTool):
    name: str = "llm"
    description: str = "Useful for answering general questions that don't fit other tools"
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool to get an answer from the LLM."""
        # Get Groq API key from config
        api_key = Config.GROQ_API_KEY
        
        if not api_key or api_key == "your_groq_api_key_here":
            # Return mock response if no API key is provided
            return f"Based on general knowledge, the answer to '{query}' is a placeholder response from the LLM tool."
        
        try:
            client = Groq(api_key=api_key)
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    }
                ],
                model=Config.DEFAULT_GROQ_MODEL,  # Using a free model from Groq
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Asynchronous version of the tool."""
        return self._run(query, run_manager=run_manager)