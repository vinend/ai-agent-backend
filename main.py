from app import create_app
import os
from app.config import Config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Validate API keys on startup
missing_keys = Config.validate_keys()
if missing_keys:
    print(f"Warning: Missing or invalid API keys: {', '.join(missing_keys)}")
    print("Please update the .env file with your API keys.")

# Create the Flask app and SocketIO instance
app, socketio = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Check if running in development or production
    import os
    is_development = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    if is_development:
        socketio.run(app, host='0.0.0', port=port, debug=True)
    else:
        # For production, allow unsafe Werkzeug
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)