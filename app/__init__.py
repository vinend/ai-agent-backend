from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Import and register blueprints
    from app.endpoints.query import query_bp
    from app.endpoints.streaming import streaming_bp, register_socketio_events
    
    app.register_blueprint(query_bp)
    app.register_blueprint(streaming_bp)
    
    # Register SocketIO events
    register_socketio_events(socketio)
    
    return app, socketio