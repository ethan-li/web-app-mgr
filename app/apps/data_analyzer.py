import time
import threading
from typing import Dict, Any, List
import base64
from io import BytesIO
import os
import json

import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive Agg
import matplotlib.pyplot as plt
import numpy as np

from app.core.base_app import BaseApp

class DataAnalyzer(BaseApp):
    def __init__(self, app_id: str, app_dir: str, config_dir: str, intermediate_dir: str, output_dir: str):
        super().__init__(app_id, app_dir, config_dir, intermediate_dir, output_dir)
        self.required_configs = ["data", "analysis"]
        self.config_data_analyzer = None
        self.analysis_thread = None
        self.raw_data = None
        self.analysis_results = None
        self.progress = 0
        self.current_plot = None
        
    def validate_configs(self) -> bool:
        if self.configs is None or self.configs.get("default") is None:
            return False

        self.config_data_analyzer = self.configs["default"]

        """Validate configuration files"""
        if not all(config in self.config_data_analyzer for config in self.required_configs):
            return False
            
        # Validate data configuration
        data_config = self.config_data_analyzer["data"]
        if "values" not in data_config or not isinstance(data_config["values"], list):
            return False
            
        # Validate analysis configuration
        analysis_config = self.config_data_analyzer["analysis"]
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
            
            # Save plot to memory and file
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight')
            plt.close(fig)  # Explicitly close the figure
            
            # Save plot to file
            self.save_output_file("histogram.png", buffer.getvalue())
            
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"Error creating histogram: {str(e)}")
            return None
        
    def _analyze_data(self):
        """Analyze data in background thread"""
        try:
            # Get data and save it
            self.raw_data = np.array(self.config_data_analyzer["data"]["values"])
            self.save_intermediate_file("raw_data.json", self.raw_data.tolist())
            self.progress = 20
            
            # Initialize results
            self.analysis_results = {}
            metrics = self.config_data_analyzer["analysis"]["metrics"]
            
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
                
            # Save intermediate results
            self.save_intermediate_file("partial_results.json", self.analysis_results)
            
            # Generate histogram
            if "histogram" in metrics:
                self.current_plot = self._create_histogram(self.raw_data)
                
            # Save final results
            self.save_output_file("analysis_results.json", {
                "data_info": {
                    "sample_size": len(self.raw_data),
                    "data_range": [float(np.min(self.raw_data)), float(np.max(self.raw_data))]
                },
                "analysis_results": self.analysis_results,
                "processing_time": "2 seconds"
            })
            
            # Simulate processing time
            time.sleep(2)
            self.progress = 100
            
        except Exception as e:
            self.progress = -1
            # Save error information
            self.save_output_file("error.txt", str(e))
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
            
        # Load final results
        results_path = os.path.join(self.output_dir, "analysis_results.json")
        with open(results_path, "r") as f:
            results = json.load(f)
            
        # Load histogram if exists
        histogram_path = os.path.join(self.output_dir, "histogram.png")
        if os.path.exists(histogram_path):
            with open(histogram_path, "rb") as f:
                results["plot"] = base64.b64encode(f.read()).decode()
                
        # Add output files information
        results["output_files"] = {
            "data": "raw_data.json",
            "results": "analysis_results.json",
            "plot": "histogram.png",
            "intermediate_files": [
                "partial_results.json"
            ]
        }
            
        return results
    
    