from typing import Dict, Type, Optional
import uuid
import os

from .base_app import BaseApp

class AppManager:
    def __init__(self, runtime_dir: str = "runtime"):
        self.apps: Dict[str, BaseApp] = {}
        self.app_types: Dict[str, Type[BaseApp]] = {}
        self.runtime_dir = os.path.abspath(runtime_dir)
        
        # Create runtime directory if it doesn't exist
        if not os.path.exists(self.runtime_dir):
            os.makedirs(self.runtime_dir)
        
    def register_app_type(self, app_type_name: str, app_class: Type[BaseApp]) -> None:
        """Register application type"""
        self.app_types[app_type_name] = app_class
        
    def create_app_instance(self, app_type_name: str) -> str:
        """Create application instance"""
        if app_type_name not in self.app_types:
            raise ValueError(f"Unknown application type: {app_type_name}")
            
        app_id = str(uuid.uuid4())
        
        # Create app directory structure
        app_dir = os.path.join(self.runtime_dir, app_id)
        config_dir = os.path.join(app_dir, "config")
        intermediate_dir = os.path.join(app_dir, "intermediate")
        output_dir = os.path.join(app_dir, "output")
        
        # Create directories
        os.makedirs(app_dir)
        os.makedirs(config_dir)
        os.makedirs(intermediate_dir)
        os.makedirs(output_dir)
        
        # Create app instance with directory paths
        app_instance = self.app_types[app_type_name](
            app_id,
            app_dir=app_dir,
            config_dir=config_dir,
            intermediate_dir=intermediate_dir,
            output_dir=output_dir
        )
        self.apps[app_id] = app_instance
        return app_id
        
    def get_app(self, app_id: str) -> Optional[BaseApp]:
        """Get application instance"""
        return self.apps.get(app_id)
        
    def delete_app(self, app_id: str) -> None:
        """Delete application instance"""
        if app_id in self.apps:
            app = self.apps[app_id]
            if app.is_running:
                app.stop()
            
            # Clean up app directory
            app_dir = os.path.join(self.runtime_dir, app_id)
            if os.path.exists(app_dir):
                import shutil
                shutil.rmtree(app_dir)
            
            del self.apps[app_id]
            
    def get_all_apps(self) -> Dict[str, BaseApp]:
        """Get all application instances"""
        return self.apps.copy()
        
    def get_app_types(self) -> Dict[str, Type[BaseApp]]:
        """Get all registered application types"""
        return self.app_types.copy() 
    
    