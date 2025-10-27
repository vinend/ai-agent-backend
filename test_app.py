import requests
import json

# Test the application with various queries
def test_app():
    base_url = "http://localhost:5000"
    
    # Test queries
    test_queries = [
        {"query": "So, how's is it looking in the sky up Bogor, Indonesia?"},
        {"query": "What is 2*4+1?"},
        {"query": "Who is the president of Italy right now?"},
        {"query": "What is 15 + 25?"},
        {"query": "How to make an Iceland Volcano Baked cake?"},
        {"query": "What's the temperature in Cape Town?"},
        {"query": "What is 10 / 4?"},
        {"query": "Who is nelson laurensius Universitas Indonesia?"},
    ]
    
    print("Testing the AI Agent Backend Application...\n")
    
    for i, query_data in enumerate(test_queries, 1):
        print(f"Test {i}: {query_data['query']}")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                json=query_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Tool used: {result['tool_used']}")
                print(f"  Result: {result['result']}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  Exception: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_app()