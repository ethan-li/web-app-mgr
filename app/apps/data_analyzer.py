import time
import threading
from typing import Dict, Any, List
import base64
from io import BytesIO

import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive Agg
import matplotlib.pyplot as plt
import numpy as np

from app.core.base_app import BaseApp

class DataAnalyzer(BaseApp):
    def __init__(self, app_id: str):
        super().__init__(app_id)
        self.required_configs = ["data", "analysis"]
        self.analysis_thread = None
        self.raw_data = None
        self.analysis_results = None
        self.progress = 0
        self.current_plot = None
        
    def validate_configs(self) -> bool:
        """Validate configuration files"""
        if not all(config in self.configs for config in self.required_configs):
            return False
            
        # Validate data configuration
        data_config = self.configs["data"]
        if "values" not in data_config or not isinstance(data_config["values"], list):
            return False
            
        # Validate analysis configuration
        analysis_config = self.configs["analysis"]
        if "metrics" not in analysis_config or not isinstance(analysis_config["metrics"], list):
            return False
            
        valid_metrics = {"mean", "median", "std", "histogram"}
        if not all(metric in valid_metrics for metric in analysis_config["metrics"]):
            return False
            
        return True
        
    def _create_histogram(self, data: np.ndarray) -> str:
        """Create histogram and return as base64 encoded string"""
        try:
            # Create a new figure with specified backend
            fig = plt.figure(figsize=(10, 6))
            plt.hist(data, bins=30, edgecolor='black')
            plt.title('Data Distribution Histogram')
            plt.xlabel('Value')
            plt.ylabel('Frequency')
            
            # Save plot to memory
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight')
            plt.close(fig)  # Explicitly close the figure
            
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"Error creating histogram: {str(e)}")
            return None
        
    def _analyze_data(self):
        """Analyze data in background thread"""
        try:
            # Get data
            self.raw_data = np.array(self.configs["data"]["values"])
            self.progress = 20
            
            # Initialize results
            self.analysis_results = {}
            metrics = self.configs["analysis"]["metrics"]
            
            # Calculate basic statistics
            if "mean" in metrics:
                self.analysis_results["mean"] = float(np.mean(self.raw_data))
                self.progress = 40
                
            if "median" in metrics:
                self.analysis_results["median"] = float(np.median(self.raw_data))
                self.progress = 60
                
            if "std" in metrics:
                self.analysis_results["std"] = float(np.std(self.raw_data))
                self.progress = 80
                
            # Generate histogram
            if "histogram" in metrics:
                self.current_plot = self._create_histogram(self.raw_data)
                
            # Simulate processing time
            time.sleep(2)
            self.progress = 100
            
        except Exception as e:
            self.progress = -1
            print(f"Error in _analyze_data: {str(e)}")  # Add error logging
            raise e
            
    def start(self) -> None:
        """Start data analysis"""
        if self.is_running:
            raise RuntimeError("Application is already running")
            
        self.progress = 0
        self.analysis_thread = threading.Thread(target=self._analyze_data)
        self.analysis_thread.start()
        self.is_running = True
        
    def stop(self) -> None:
        """Stop data analysis"""
        if not self.is_running:
            raise RuntimeError("Application is not running")
            
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=1)
            
        self.is_running = False
        self.progress = 0
        
    def get_status(self) -> Dict[str, Any]:
        """Get analysis status"""
        status = {
            "progress": self.progress,
            "is_running": self.is_running,
            "app_type": "data_analyzer"
        }
        
        # If there are partial results, add to status
        if self.analysis_results:
            status["partial_results"] = self.analysis_results
            
        # If there's a plot, add to status
        if self.current_plot:
            status["plot"] = self.current_plot
            
        return status
        
    def get_report(self) -> Dict[str, Any]:
        """Get analysis report"""
        if not self.analysis_results or self.progress < 100:
            return {"error": "Analysis not completed"}
            
        return {
            "data_info": {
                "sample_size": len(self.raw_data),
                "data_range": [float(np.min(self.raw_data)), float(np.max(self.raw_data))]
            },
            "analysis_results": self.analysis_results,
            "plot": self.current_plot if self.current_plot else None,
            "processing_time": "2 seconds"  # In a real application, should record actual processing time
        } 
    
    