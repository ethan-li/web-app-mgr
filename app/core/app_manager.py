from typing import Dict, Type, Optional
import uuid

from .base_app import BaseApp

class AppManager:
    def __init__(self):
        self.apps: Dict[str, BaseApp] = {}
        self.app_types: Dict[str, Type[BaseApp]] = {}
        
    def register_app_type(self, app_type_name: str, app_class: Type[BaseApp]) -> None:
        """Register application type"""
        self.app_types[app_type_name] = app_class
        
    def create_app_instance(self, app_type_name: str) -> str:
        """Create application instance"""
        if app_type_name not in self.app_types:
            raise ValueError(f"Unknown application type: {app_type_name}")
            
        app_id = str(uuid.uuid4())
        app_instance = self.app_types[app_type_name](app_id)
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
            del self.apps[app_id]
            
    def get_all_apps(self) -> Dict[str, BaseApp]:
        """Get all application instances"""
        return self.apps.copy()
        
    def get_app_types(self) -> Dict[str, Type[BaseApp]]:
        """Get all registered application types"""
        return self.app_types.copy() 
    
    