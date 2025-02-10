from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class BaseApp(ABC):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.configs: Dict[str, Dict] = {}
        self.is_running = False
        
    def upload_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Upload configuration file"""
        self.configs[config_name] = config_data
        
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get configuration file"""
        return self.configs.get(config_name, {})
        
    @abstractmethod
    def validate_configs(self) -> bool:
        """Validate all configuration files"""
        pass
        
    @abstractmethod
    def start(self) -> None:
        """Start the application"""
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Stop the application"""
        pass
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current application status"""
        pass
        
    @abstractmethod
    def get_report(self) -> Dict[str, Any]:
        """Get application execution report"""
        pass 

    