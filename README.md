# AI Agent Backend Application

**Author:** Andi Alvin  
**Date of Creation:** October 20, 2025

## Overview

This is a backend application that routes user queries to different tools (weather, math, LLM) using LangChain for tool selection. The application provides both REST API endpoints and WebSocket streaming capabilities. It simulates the core of an AI agent architecture, automatically determining which specialized tool to use based on the user's natural language query.

## Features

- **Natural Language Query Processing**: Accepts queries in natural language format
- **Intelligent Tool Routing**: Automatically routes queries to the appropriate tool
- **Multiple Tool Support**: Weather, Math, and LLM tools
- **REST API**: Standard HTTP endpoints for integration
- **Streaming Support**: Server-sent events and WebSocket capabilities
- **Configurable**: Environment-based configuration for API keys
- **Mock Responses**: Fallback responses when API keys are not configured

## Architecture

The application follows a modular architecture with the following components:

```
app/
├── __init__.py          # Flask app initialization
├── config.py           # Configuration management
├── tools/              # Tool implementations
│   ├── __init__.py
│   ├── weather_tool.py # Weather data retrieval
│   ├── math_tool.py    # Mathematical operations
│   └── llm_tool.py     # LLM-based responses
├── endpoints/          # API route definitions
│   ├── __init__.py
│   ├── query.py        # Main query endpoint
│   └── streaming.py    # Streaming endpoints
└── utils/              # Utility functions
    ├── __init__.py
    └── tool_selector.py # Tool selection logic
```

## Installation

### Prerequisites

- Python 3.1.3 or higher
- API keys for Groq and OpenWeatherMap (optional, mock responses available)

### Setup

1. **Clone the repository** (if applicable) or create the project structure

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys to the `.env` file (see Environment Variables section)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

**Note**: If API keys are not provided, the application will use mock responses for testing purposes.

## API Endpoints

### POST /query

Accepts a JSON payload with a query and returns the result from the appropriately selected tool.

#### Request Format
```json
{
  "query": "What's the weather like in Paris?"
}
```

#### Response Format
```json
{
  "query": "What's the weather like in Paris?",
  "tool_used": "weather",
  "result": "It's 26°C and sunny in Paris."
}
```

#### Example Queries
- Weather: `"What's the weather today in San Francisco?"`
- Math: `"What is 42 * 7?"`
- General: `"Who is the president of France?"`

### POST /stream

Streams the response for a query using server-sent events.

#### Request Format
```json
{
  "query": "What is 24 * 5?"
}
```

#### Response
Server-sent events with the result in the same format as the `/query` endpoint.

### WebSocket Events

The application also supports WebSocket connections for real-time communication:

- **Event: 'query'** - Send a query object: `{"query": "your question"}`
- **Event: 'result'** - Receive the result from the tool
- **Event: 'error'** - Receive error messages

## Tools

### Weather Tool

- **Purpose**: Fetches weather information for a specific city
- **API Used**: OpenWeatherMap API
- **Model**: Uses keyword detection to identify weather-related queries
- **Fallback**: Provides mock weather data when API key is not configured

### Math Tool

- **Purpose**: Performs basic mathematical operations
- **Operations Supported**: Addition, subtraction, multiplication, division
- **Parsing**: Extracts mathematical expressions from natural language
- **Examples**: "What is 42 * 7?", "Calculate 15 + 25"

### LLM Tool

- **Purpose**: Answers general questions that don't fit other tools
- **Model Used**: Groq's Llama3-8b-8192 model
- **Configuration**: 
  - Temperature: 0 (for more deterministic responses)
  - Model: llama3-8b-8192 (free tier model)
- **Fallback**: Provides mock responses when API key is not configured

## Groq API Configuration

The application uses Groq's API with the following settings:

- **Model**: `llama3-8b-8192`
- **Temperature**: `0` (for consistent, deterministic responses)
- **API Key**: Configured via `GROQ_API_KEY` environment variable
- **Usage**: For general questions that don't match weather or math patterns

The Llama3-8b-8192 model is chosen for its balance of performance and cost-effectiveness, providing reliable responses for general knowledge questions.

## Tool Selection Logic

The application uses a keyword-based routing system to determine which tool to use:

1. **Weather Detection**: Looks for keywords like "weather", "temperature", "rain", "sunny", "cloudy", "hot", "cold"
2. **Math Detection**: Looks for mathematical operators (+, -, *, x, /) and numeric values
3. **LLM Fallback**: All other queries are routed to the LLM tool

This approach provides reliable routing without requiring complex NLP models, making the system lightweight and efficient.

## Usage Examples

### With Postman

1. Set method to `POST` with URL `http://localhost:5000/query`
2. Set header: `Content-Type: application/json`
3. Add JSON body with query: `{"query": "your question here"}`
4. Send request and receive structured response

### With cURL

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 24 * 5?"}'
```

### Programmatic Usage

```python
import requests

response = requests.post(
    "http://localhost:5000/query",
    json={"query": "What's the weather in Tokyo?"},
    headers={"Content-Type": "application/json"}
)

data = response.json()
print(f"Tool used: {data['tool_used']}")
print(f"Result: {data['result']}")
```

## Running the Application

To start the application:

```bash
python main.py
```

The application will start on `http://localhost:5000` by default.

### Development Mode
The application runs in debug mode by default, which is helpful for development but should be disabled in production.

## Testing

The application includes a test script (`test_app.py`) that demonstrates various query types:

- Weather queries
- Mathematical calculations
- General knowledge questions

To run the tests:

```bash
python test_app.py
```

## Dependencies

- **Flask**: Web framework for creating the API
- **Flask-SocketIO**: WebSocket support for real-time communication
- **langchain**: Tool orchestration and management
- **langchain-groq**: Integration with Groq's API
- **groq**: Direct API client for Groq services
- **requests**: HTTP requests for weather API
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management

## Configuration Details

The application uses a configuration module (`app/config.py`) that:

- Loads environment variables from `.env` file
- Validates that required API keys are present
- Provides default values for testing
- Issues warnings if API keys are missing or invalid

## Query Examples and Output

The application handles various types of queries with appropriate tool routing:

### Weather Queries
- "What's the weather today in San Francisco?"
- "How's the temperature in Tokyo?"
- "Is it raining in London?"

### Math Queries
- "What is 42 * 7?"
- "What is 15 + 25?"
- "Calculate 100 / 4"

### General Questions
- "Who is the president of France?"
- "Tell me a joke"
- "How does photosynthesis work?"

## Test Results
![image](https://hackmd.io/_uploads/S1A9cYQCll.png)
![image](https://hackmd.io/_uploads/HJgysYQAxg.png)
![image](https://hackmd.io/_uploads/ryx-jYXAlg.png)
![image](https://hackmd.io/_uploads/BypXiYm0ge.png)
![image](https://hackmd.io/_uploads/S1rPoFmAge.png)
## Error Handling

The application includes comprehensive error handling:

- Invalid queries return appropriate error messages
- API failures are caught and handled gracefully
- Missing API keys result in informative warnings
- Network errors are managed without crashing the application

## Performance Considerations

- The application uses keyword-based routing for fast tool selection
- Mock responses are available when external APIs are not configured
- Asynchronous operations are supported where appropriate
- Memory usage is optimized for concurrent requests

## Security

- API keys are loaded from environment variables, not hardcoded
- Input validation is performed on all queries
- CORS is configured to allow appropriate origins
- No sensitive data is logged in production mode

