import os

from app.core.flask_service import FlaskWebService
from app.core.fastapi_service import FastAPIWebService
from app.apps.image_processor import ImageProcessor
from app.apps.data_analyzer import DataAnalyzer

# Map of type_name -> app class; add new apps here
_APP_CLASSES = [ImageProcessor, DataAnalyzer]


def create_app(framework="flask"):
    """Create a web service instance and register all known app types."""
    if framework.lower() == "flask":
        service = FlaskWebService()
    elif framework.lower() == "fastapi":
        service = FastAPIWebService()
    else:
        raise ValueError(f"Unsupported framework: {framework}")

    # Register each app type in both the manager and the registry
    for app_class in _APP_CLASSES:
        meta = app_class.get_metadata()
        service.app_manager.register_app_type(meta.type_name, app_class)
        service.app_registry.register(meta)

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


