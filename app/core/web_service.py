from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .app_manager import AppManager

class WebService(ABC):
    def __init__(self):
        self.app_manager = AppManager()
        
    @abstractmethod
    def create_app(self, app_type: str) -> Dict[str, Any]:
        """Create application instance"""
        pass
        
    @abstractmethod
    def delete_app(self, app_id: str) -> Dict[str, Any]:
        """Delete application instance"""
        pass
        
    @abstractmethod
    def upload_config(self, app_id: str, config_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload configuration file"""
        pass
        
    @abstractmethod
    def start_app(self, app_id: str) -> Dict[str, Any]:
        """Start application"""
        pass
        
    @abstractmethod
    def stop_app(self, app_id: str) -> Dict[str, Any]:
        """Stop application"""
        pass
        
    @abstractmethod
    def get_app_status(self, app_id: str) -> Dict[str, Any]:
        """Get application status"""
        pass
        
    @abstractmethod
    def get_app_report(self, app_id: str) -> Dict[str, Any]:
        """Get application report"""
        pass
        
    @abstractmethod
    def get_app_types(self) -> Dict[str, Any]:
        """Get all available application types"""
        pass
        
    @abstractmethod
    def get_all_apps(self) -> Dict[str, Any]:
        """Get all application instances"""
        pass
        
    def _get_app_or_error(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get application instance or return error message if not exists"""
        app = self.app_manager.get_app(app_id)
        if app is None:
            return {"error": f"Application not found: {app_id}"}
        return None 
    
    