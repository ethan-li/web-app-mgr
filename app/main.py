import os

from app.core.flask_service import FlaskWebService
from app.core.fastapi_service import FastAPIWebService
from app.apps.image_processor import ImageProcessor
from app.apps.data_analyzer import DataAnalyzer

def create_app(framework="flask"):
    """Create a web service instance"""
    if framework.lower() == "flask":
        service = FlaskWebService()
    elif framework.lower() == "fastapi":
        service = FastAPIWebService()
    else:
        raise ValueError(f"Unsupported framework: {framework}")
        
    # Register application types
    service.app_manager.register_app_type("image_processor", ImageProcessor)
    service.app_manager.register_app_type("data_analyzer", DataAnalyzer)
    
    return service
    
def main():
    """Main entry point"""
    # Get configuration from environment variables
    framework = os.getenv("FRAMEWORK", "flask").lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    
    # Create service instance
    service = create_app(framework)
    
    # Start service
    print(f"Starting service with {framework} framework")
    print(f"Service running at http://{host}:{port}")
    service.run(host=host, port=port)
    
if __name__ == "__main__":
    main() 


