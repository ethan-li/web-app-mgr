import os
import argparse

from app.core.flask_service import FlaskWebService
from app.core.fastapi_service import FastAPIWebService
from app.apps.image_processor import ImageProcessor
from app.apps.data_analyzer import DataAnalyzer

def create_app(framework="flask", runtime_dir="runtime"):
    """Create a web service instance"""
    if framework.lower() == "flask":
        service = FlaskWebService(runtime_dir=runtime_dir)
    elif framework.lower() == "fastapi":
        service = FastAPIWebService(runtime_dir=runtime_dir)
    else:
        raise ValueError(f"Unsupported framework: {framework}")
        
    # Register application types
    service.app_manager.register_app_type("image_processor", ImageProcessor)
    service.app_manager.register_app_type("data_analyzer", DataAnalyzer)
    
    return service
    
def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Web Service Manager")
    parser.add_argument("--framework", default="flask", choices=["flask", "fastapi"],
                      help="Web framework to use (default: flask)")
    parser.add_argument("--host", default="0.0.0.0",
                      help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000,
                      help="Port to bind to (default: 5000)")
    parser.add_argument("--runtime-dir", default="runtime",
                      help="Directory for runtime files (default: runtime)")
    
    args = parser.parse_args()
    
    # Override with environment variables if set
    framework = os.getenv("FRAMEWORK", args.framework).lower()
    host = os.getenv("HOST", args.host)
    port = int(os.getenv("PORT", args.port))
    runtime_dir = os.getenv("RUNTIME_DIR", args.runtime_dir)
    
    # Create service instance
    service = create_app(framework, runtime_dir)
    
    # Start service
    print(f"Starting service with {framework} framework")
    print(f"Service running at http://{host}:{port}")
    print(f"Runtime directory: {runtime_dir}")
    service.run(host=host, port=port)
    
if __name__ == "__main__":
    main() 


