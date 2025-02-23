from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
import os
import json

class BaseApp(ABC):
    def __init__(self, app_id: str, app_dir: str, config_dir: str, intermediate_dir: str, output_dir: str):
        self.app_id = app_id
        self.app_dir = app_dir
        self.config_dir = config_dir
        self.intermediate_dir = intermediate_dir
        self.output_dir = output_dir
        self.configs: Dict[str, Dict] = {}
        self.is_running = False
        
    def upload_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Upload configuration file"""
        print(f"config_name={config_name}")
        self.configs[config_name] = config_data
        
        # Save config to file
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get configuration file"""
        if config_name not in self.configs:
            # Try to load from file
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.configs[config_name] = json.load(f)
        return self.configs.get(config_name, {})
        
    def save_intermediate_file(self, filename: str, content: Any) -> str:
        """Save intermediate file"""
        file_path = os.path.join(self.intermediate_dir, filename)
        if isinstance(content, (dict, list)):
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, bytes):
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            with open(file_path, "w") as f:
                f.write(str(content))
        return file_path
        
    def save_output_file(self, filename: str, content: Any) -> str:
        """Save output file"""
        file_path = os.path.join(self.output_dir, filename)
        if isinstance(content, (dict, list)):
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, bytes):
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            with open(file_path, "w") as f:
                f.write(str(content))
        return file_path
        
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

    